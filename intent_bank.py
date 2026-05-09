import hashlib
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional

from bot_core import normalize, get_state

from app_paths import BASE_DIR
PATTERNS_PATH = BASE_DIR / "intent_patterns.json"
TEMPLATES_PATH = BASE_DIR / "response_templates.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
UNKNOWN_PATH = BASE_DIR / "unknown_messages.jsonl"
UNKNOWN_INDEX_PATH = BASE_DIR / "unknown_messages_index.json"

DIRECT_BANK_INTENTS = {
    "greeting_more_info",
    "price_final",
    "warranty_question",
    "new_or_used",
    "real_photo_request",
    "opening_hours",
    "trust_reassurance",
    "human_request",
    "after_sale_problem",
    "bulk_or_wholesale",
    "compare_models",
    "restaurant_menu",
    "payment_question",
    "order_start",
    "delivery_question",
    "location_question"
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def settings() -> Dict[str, Any]:
    return load_json(SETTINGS_PATH, {})

def patterns_data() -> Dict[str, Any]:
    return load_json(PATTERNS_PATH, {"version": "4.3", "default_threshold": 4, "intents": []})

def templates_data() -> Dict[str, Any]:
    return load_json(TEMPLATES_PATH, {"version": "4.3", "templates": {}})

def msg_hash(message: str) -> str:
    return hashlib.sha1(normalize(message).encode("utf-8")).hexdigest()[:16]

def render_template(template_id: str, state: Dict[str, Any]) -> str:
    data = templates_data()
    txt = data.get("templates", {}).get(template_id, "")

    s = settings()
    values = {
        "business_name": s.get("business_name", "O'CG / BZ STORE"),
        "city": s.get("city", "Brazzaville"),
        "whatsapp": s.get("whatsapp", "+242050541963"),
        "phone": s.get("phone", "+242066518669"),
        "campaign_label": state.get("campaign_label", ""),
        "campaign_category": state.get("campaign_category", "")
    }

    for k, v in values.items():
        txt = txt.replace("{" + k + "}", str(v))

    return txt.replace('\\n', '\n').strip()

def score_intent(message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
    msg_norm = normalize(message)
    score = 0
    matched = {
        "patterns": [],
        "keywords": [],
        "examples": []
    }

    for pat in intent.get("patterns", []) or []:
        try:
            if re.search(pat, msg_norm):
                score += 4
                matched["patterns"].append(pat)
        except re.error:
            continue

    for kw in intent.get("keywords", []) or []:
        kw_norm = normalize(kw)
        if kw_norm and kw_norm in msg_norm:
            score += 2
            matched["keywords"].append(kw)

    for ex in intent.get("examples", []) or []:
        ex_norm = normalize(ex)
        if not ex_norm:
            continue
        ratio = SequenceMatcher(None, msg_norm, ex_norm).ratio()
        if ex_norm in msg_norm or msg_norm in ex_norm or ratio >= 0.82:
            score += 3
            matched["examples"].append(ex)

    priority = int(intent.get("priority", 50))
    weighted = score + (priority / 100.0)

    return {
        "intent": intent,
        "score": score,
        "weighted": weighted,
        "matched": matched
    }

def match_intent(message: str) -> Optional[Dict[str, Any]]:
    data = patterns_data()
    default_threshold = int(data.get("default_threshold", 4))

    candidates = []
    for intent in data.get("intents", []) or []:
        sc = score_intent(message, intent)
        threshold = int(intent.get("threshold", default_threshold))
        if sc["score"] >= threshold:
            candidates.append(sc)

    if not candidates:
        return None

    candidates.sort(key=lambda x: x["weighted"], reverse=True)
    best = candidates[0]
    score = best["score"]

    confidence = min(0.96, 0.55 + (score * 0.06))

    return {
        "intent_id": best["intent"].get("id"),
        "label": best["intent"].get("label"),
        "template": best["intent"].get("template"),
        "safe_to_auto_send": bool(best["intent"].get("safe_to_auto_send", True)),
        "score": score,
        "confidence": round(confidence, 2),
        "matched": best["matched"],
        "candidates": [
            {
                "intent_id": c["intent"].get("id"),
                "label": c["intent"].get("label"),
                "score": c["score"],
                "matched": c["matched"]
            }
            for c in candidates[:5]
        ]
    }

def try_intent_bank_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = match_intent(message)
    if not m:
        return None

    reply = render_template(m["template"], state)
    if not reply:
        return None

    return {
        "reply": reply,
        "confidence": m["confidence"],
        "intent": "bank_" + str(m["intent_id"]),
        "bank_intent_id": m["intent_id"],
        "safe_to_auto_send": m["safe_to_auto_send"],
        "debug": {
            "source": "intent_bank",
            "score": m["score"],
            "matched": m["matched"],
            "candidates": m["candidates"]
        }
    }

def should_return_bank_before_product(bank_result: Optional[Dict[str, Any]]) -> bool:
    if not bank_result:
        return False
    intent_id = bank_result.get("bank_intent_id", "")
    return intent_id in DIRECT_BANK_INTENTS

def record_unknown_message(message: str, chat_id: str, reason: str, state: Dict[str, Any], result: Dict[str, Any]):
    msg_norm = normalize(message)
    if not msg_norm or len(msg_norm) < 2:
        return

    h = msg_hash(message)
    index = load_json(UNKNOWN_INDEX_PATH, {})

    if h in index:
        index[h]["count"] = int(index[h].get("count", 1)) + 1
        index[h]["last_seen"] = now()
        save_json(UNKNOWN_INDEX_PATH, index)
        return

    row = {
        "hash": h,
        "time": now(),
        "chat_id": chat_id,
        "message": message,
        "normalized": msg_norm,
        "reason": reason,
        "state": {
            "campaign_id": state.get("campaign_id", ""),
            "campaign_label": state.get("campaign_label", ""),
            "last_category": state.get("last_category", ""),
            "last_product_id": state.get("last_product_id", "")
        },
        "result_intent": result.get("intent", ""),
        "result_confidence": result.get("confidence", 0),
        "status": "waiting_learning"
    }

    with UNKNOWN_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    index[h] = {
        "hash": h,
        "first_seen": row["time"],
        "last_seen": row["time"],
        "count": 1,
        "status": "waiting_learning"
    }
    save_json(UNKNOWN_INDEX_PATH, index)

def explain_match(message: str) -> Dict[str, Any]:
    m = match_intent(message)
    return {
        "message": message,
        "normalized": normalize(message),
        "match": m
    }
