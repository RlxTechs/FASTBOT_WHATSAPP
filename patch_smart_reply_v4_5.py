from pathlib import Path

p = Path("smart_reply.py")
txt = p.read_text(encoding="utf-8-sig")

guard = r'''
def is_facebook_generic_more_info(msg_norm: str) -> bool:
    checks = [
        "puis je en savoir plus",
        "je peux en savoir plus",
        "en savoir plus",
        "plus a ce sujet",
        "plus à ce sujet",
        "ce sujet"
    ]
    return any(x in msg_norm for x in checks)
'''

if "def is_facebook_generic_more_info" not in txt:
    insert_after = "def is_greeting(msg_norm: str) -> bool:"
    idx = txt.find(insert_after)
    if idx >= 0:
        txt = txt[:idx] + guard + "\n" + txt[idx:]

needle = '''    has_campaign_context = bool(state.get("campaign_id") or state.get("campaign_label"))'''

patch = '''    has_campaign_context = bool(state.get("campaign_id") or state.get("campaign_label"))

    # Sécurité V4.5 :
    # Si le client dit “en savoir plus à ce sujet” mais qu’aucune pub n’est classée,
    # on ne répond pas avec une phrase vague. On attend l’analyse de la carte Facebook.
    if is_facebook_generic_more_info(msg_norm) and not has_campaign_context:
        result = {
            "reply": "",
            "confidence": 0.0,
            "intent": "waiting_facebook_campaign_context",
            "safe_to_auto_send": False,
            "debug": {
                "blocked_reason": "Generic Facebook greeting requires campaign context before replying"
            }
        }
        record_unknown_message(message, chat_id, "facebook_more_info_without_campaign_context", state, result)
        return result'''

if needle in txt and "waiting_facebook_campaign_context" not in txt:
    txt = txt.replace(needle, patch)

p.write_text(txt, encoding="utf-8")
print("smart_reply.py sécurisé contre les réponses vagues Facebook.")
