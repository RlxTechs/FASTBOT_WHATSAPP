from pathlib import Path
import re

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

# Imports
if "from runtime_message_reader import get_actionable_incoming_messages" not in txt:
    txt = txt.replace(
        "from conversation_guard import clean_recent_messages",
        "from conversation_guard import clean_recent_messages\nfrom runtime_message_reader import get_actionable_incoming_messages"
    )

if "from runtime_priority_rules import try_priority_reply" not in txt:
    txt = txt.replace(
        "from sales_safety_filters import classify_pre_reply",
        "from sales_safety_filters import classify_pre_reply\nfrom runtime_priority_rules import try_priority_reply"
    )

# Remplacer lecture messages
old = '''recent_messages = read_unanswered_incoming_messages(driver, limit=14)
            recent_messages = clean_recent_messages(recent_messages, chat_title)'''

new = '''recent_messages = get_actionable_incoming_messages(driver, chat_title, limit=45)'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc read_unanswered + clean non trouvé exactement. Recherche alternative...")
    txt = txt.replace(
        "recent_messages = read_unanswered_incoming_messages(driver, limit=14)",
        "recent_messages = get_actionable_incoming_messages(driver, chat_title, limit=45)"
    )
    txt = txt.replace(
        "recent_messages = clean_recent_messages(recent_messages, chat_title)",
        ""
    )

# Ajouter règles prioritaires avant classify_pre_reply
old2 = '''pre_filter = classify_pre_reply(combined_msg, last_msg, chat_title)
            if pre_filter:
                result = pre_filter
            else:
                result = generate_human_sales_reply(combined_msg, chat_title)'''

new2 = '''priority = try_priority_reply(combined_msg, last_msg, chat_title)
            if priority:
                result = priority
            else:
                pre_filter = classify_pre_reply(combined_msg, last_msg, chat_title)
                if pre_filter:
                    result = pre_filter
                else:
                    result = generate_human_sales_reply(combined_msg, chat_title)'''

if old2 in txt:
    txt = txt.replace(old2, new2)
else:
    print("⚠️ Bloc classify_pre_reply non trouvé exactement.")

# Pub inconnue : ne plus bloquer par défaut
pattern = r'''if camp\.get\("unknown"\):.*?return "unknown_campaign_blocked"'''

replacement = '''if camp.get("unknown"):
        h = camp.get("hash", "")
        block_unknown = bool(settings.get("block_on_unknown_campaign", False))

        set_state(chat_title, {
            "needs_campaign_label": block_unknown,
            "unknown_campaign_hash": h,
            "unknown_campaign_source": camp.get("source", "facebook_ad_card_unknown"),
            "unknown_campaign_image": "campaign_captures/unknown_" + str(h) + ".png"
        })

        update_cache(chat_title, "unknown_campaign_logged", {"hash": h, "no_context_attempts": 0})

        if block_unknown:
            print("⚠️ Pub inconnue détectée. Conversation bloquée en attente admin. Hash :", h)
            return "unknown_campaign_blocked"

        print("⚠️ Pub inconnue détectée mais conversation NON bloquée. Hash :", h)
        return "unknown_campaign_logged_continue"'''

if re.search(pattern, txt, flags=re.S):
    txt = re.sub(pattern, replacement, txt, flags=re.S)
else:
    print("⚠️ Bloc unknown campaign non trouvé automatiquement.")

p.write_text(txt, encoding="utf-8")
print("✅ main.py corrigé : nouveaux messages + priorités + pub inconnue non bloquante.")
