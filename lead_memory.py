import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from bot_core import normalize

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

LEADS_PATH = BASE_DIR / "lead_memory.json"

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def now_ts():
    return time.time()

def load_leads() -> Dict[str, Any]:
    try:
        if LEADS_PATH.exists():
            return json.loads(LEADS_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {"chats": {}}

def save_leads(data: Dict[str, Any]):
    LEADS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def default_lead(chat_id: str):
    return {
        "chat_id": chat_id,
        "stage": "new",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "last_incoming_text": "",
        "last_outgoing_text": "",
        "last_intent": "",
        "last_item": "",
        "last_zone": "",
        "last_phone": "",
        "last_incoming_ts": 0,
        "last_outgoing_ts": 0,
        "followup_count": 0,
        "do_not_followup": False,
        "needs_human": False,
        "history": []
    }

def get_lead(chat_id: str) -> Dict[str, Any]:
    data = load_leads()
    chats = data.setdefault("chats", {})
    if chat_id not in chats:
        chats[chat_id] = default_lead(chat_id)
        save_leads(data)
    return chats[chat_id]

def update_lead(chat_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    data = load_leads()
    chats = data.setdefault("chats", {})
    lead = chats.get(chat_id) or default_lead(chat_id)

    for k, v in patch.items():
        lead[k] = v

    lead["updated_at"] = now_iso()
    chats[chat_id] = lead
    save_leads(data)
    return lead

def append_history(chat_id: str, role: str, text: str, meta: Optional[Dict[str, Any]] = None):
    data = load_leads()
    chats = data.setdefault("chats", {})
    lead = chats.get(chat_id) or default_lead(chat_id)

    hist = lead.setdefault("history", [])
    hist.append({
        "time": now_iso(),
        "role": role,
        "text": text,
        "meta": meta or {}
    })

    if len(hist) > 80:
        lead["history"] = hist[-80:]

    lead["updated_at"] = now_iso()
    chats[chat_id] = lead
    save_leads(data)

def extract_phone(text: str) -> str:
    m = re.search(r"(\+242\s*)?0[456]\s*\d{3}\s*\d{2}\s*\d{2}", text or "")
    return m.group(0).strip() if m else ""

def remember_incoming(chat_id: str, messages: List[str]):
    if not messages:
        return

    text = "\n".join(messages).strip()
    patch = {
        "last_incoming_text": text,
        "last_incoming_ts": now_ts()
    }

    phone = extract_phone(text)
    if phone:
        patch["last_phone"] = phone

    update_lead(chat_id, patch)
    append_history(chat_id, "client", text)

def stage_from_intent(intent: str, reply: str = "") -> str:
    i = intent or ""
    r = normalize(reply)

    if i in {"sales_multi_food", "food_menu_sent", "pizza_menu_request"}:
        return "waiting_item"

    if i in {"food_specific_order_total", "food_specific_item_order"}:
        if "quartier" in r or "zone" in r:
            return "waiting_location"
        if "numéro" in r or "numero" in r:
            return "waiting_phone"
        return "waiting_confirmation"

    if i in {"location_received", "food_location_only_received", "food_location_received_need_item"}:
        return "waiting_item"

    if i in {"food_payment_confirmation", "food_preorder_tomorrow", "payment_question"}:
        return "waiting_confirmation"

    if i in {"order_confirmed"}:
        return "confirmed"

    if i in {"deleted_message_apology", "pizza_manual_availability_needed"}:
        return "needs_human"

    return ""

def remember_outgoing(chat_id: str, reply: str, intent: str, sent: bool):
    if not reply:
        return

    patch = {
        "last_outgoing_text": reply,
        "last_outgoing_ts": now_ts(),
        "last_intent": intent
    }

    stage = stage_from_intent(intent, reply)
    if stage:
        patch["stage"] = stage

    if stage == "confirmed":
        patch["do_not_followup"] = True

    if stage == "needs_human":
        patch["needs_human"] = True

    update_lead(chat_id, patch)
    append_history(chat_id, "bot", reply, {"intent": intent, "sent": sent})

def get_due_followup(chat_id: str, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    lead = get_lead(chat_id)

    if not settings.get("auto_followup_enabled", False):
        return None

    if lead.get("do_not_followup") or lead.get("needs_human"):
        return None

    if lead.get("stage") in {"confirmed", "closed", "needs_human"}:
        return None

    last_out = float(lead.get("last_outgoing_ts") or 0)
    last_in = float(lead.get("last_incoming_ts") or 0)

    if not last_out:
        return None

    if last_in > last_out:
        return None

    elapsed = now_ts() - last_out
    count = int(lead.get("followup_count", 0))

    first_delay = float(settings.get("followup_after_minutes_1", 20)) * 60
    second_delay = float(settings.get("followup_after_minutes_2", 60)) * 60

    if count == 0 and elapsed >= first_delay:
        msg = first_followup(lead.get("stage", "new"))
    elif count == 1 and elapsed >= second_delay:
        msg = second_followup()
    else:
        return None

    update_lead(chat_id, {"followup_count": count + 1})

    return {
        "reply": msg,
        "confidence": 0.91,
        "intent": "auto_followup",
        "safe_to_auto_send": True,
        "_no_media": True,
        "debug": {"source": "lead_memory", "followup_count": count + 1}
    }

def first_followup(stage: str) -> str:
    if stage in {"new", "menu_sent", "waiting_item"}:
        return (
            "Je suis toujours disponible 😊\n"
            "Vous voulez commander quel plat exactement ?\n\n"
            "Envoyez le plat + votre quartier + votre numéro, et je confirme le total."
        )

    if stage == "waiting_location":
        return (
            "Pour finaliser, envoyez juste votre quartier ou repère exact 📍\n"
            "Comme ça je confirme les frais de livraison."
        )

    if stage == "waiting_phone":
        return (
            "Il me manque juste votre numéro + repère exact pour confirmer la commande ✅"
        )

    if stage == "waiting_confirmation":
        return (
            "Je peux confirmer la commande ? ✅\n"
            "Répondez OUI si c’est bon, ou envoyez votre modification."
        )

    return "Je reste disponible si vous voulez finaliser la commande 😊"

def second_followup():
    return (
        "Petit rappel 😊\n"
        "Si vous voulez toujours commander, envoyez le plat + votre quartier + votre numéro.\n"
        "Je vous confirme le total rapidement."
    )
