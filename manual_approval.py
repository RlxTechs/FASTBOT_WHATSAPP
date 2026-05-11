import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

PENDING_PATH = BASE_DIR / "pending_orders.json"

def load_pending() -> Dict[str, Any]:
    try:
        if PENDING_PATH.exists():
            return json.loads(PENDING_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {"orders": []}

def save_pending(data: Dict[str, Any]):
    PENDING_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def create_pending_order(chat_id: str, order_type: str, client_message: str, zone: str = "", item: str = ""):
    data = load_pending()
    orders = data.setdefault("orders", [])

    # Éviter doublons ouverts sur la même conversation et même type
    for o in orders:
        if o.get("chat_id") == chat_id and o.get("status") == "pending" and o.get("order_type") == order_type:
            o["updated_at"] = datetime.now().isoformat(timespec="seconds")
            o["client_message"] = client_message
            o["zone"] = zone
            o["item"] = item
            save_pending(data)
            return o

    order = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "chat_id": chat_id,
        "order_type": order_type,
        "item": item,
        "zone": zone,
        "client_message": client_message,
        "status": "pending",
        "decision": "",
        "reply": ""
    }

    orders.append(order)
    save_pending(data)
    return order

def consume_decision(chat_id: str) -> Optional[Dict[str, Any]]:
    data = load_pending()
    changed = False

    for o in data.get("orders", []):
        if o.get("chat_id") == chat_id and o.get("status") == "ready_to_send":
            o["status"] = "sent_by_bot"
            o["sent_at"] = datetime.now().isoformat(timespec="seconds")
            changed = True
            save_pending(data)
            return {
                "reply": o.get("reply", ""),
                "confidence": 0.98,
                "intent": "operator_decision_reply",
                "safe_to_auto_send": True,
                "_no_media": True,
                "debug": {"source": "manual_approval", "order_id": o.get("id")}
            }

    if changed:
        save_pending(data)

    return None

def set_decision(order_id: str, decision: str, reply: str):
    data = load_pending()

    for o in data.get("orders", []):
        if o.get("id") == order_id:
            o["status"] = "ready_to_send"
            o["decision"] = decision
            o["reply"] = reply
            o["decided_at"] = datetime.now().isoformat(timespec="seconds")
            o["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_pending(data)
            return True

    return False
