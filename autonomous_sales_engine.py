from typing import Dict, Any

from sales_safety_filters import classify_pre_reply
from sales_director import try_sales_director
from runtime_priority_rules import try_priority_reply
from conversation_brain import generate_human_sales_reply
from lead_memory import get_lead

def no_reply(reason: str):
    return {
        "reply": "",
        "confidence": 0,
        "intent": "no_reply",
        "safe_to_auto_send": False,
        "_no_media": True,
        "debug": {"source": "autonomous_sales_engine", "reason": reason}
    }

def is_repeated_reply(chat_id: str, reply: str) -> bool:
    lead = get_lead(chat_id)
    last = (lead.get("last_outgoing_text") or "").strip()
    return bool(reply and last and reply.strip() == last)

def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:
    pre = classify_pre_reply(combined_msg, last_msg, chat_id)
    if pre:
        return pre

    director = try_sales_director(combined_msg, last_msg, chat_id)
    if director:
        if is_repeated_reply(chat_id, director.get("reply", "")):
            return no_reply("same_reply_already_sent")
        return director

    priority = try_priority_reply(combined_msg, last_msg, chat_id)
    if priority:
        if is_repeated_reply(chat_id, priority.get("reply", "")):
            return no_reply("same_reply_already_sent")
        return priority

    fallback = generate_human_sales_reply(combined_msg, chat_id)
    if fallback and is_repeated_reply(chat_id, fallback.get("reply", "")):
        return no_reply("same_reply_already_sent")

    return fallback
