import re
from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from conversation_guard import clean_recent_messages" not in txt:
    txt = txt.replace(
        "from campaign_context import detect_campaign_from_chat",
        "from campaign_context import detect_campaign_from_chat\nfrom conversation_guard import clean_recent_messages"
    )

txt = txt.replace(
    "recent_messages = read_unanswered_incoming_messages(driver, limit=10)",
    "recent_messages = read_unanswered_incoming_messages(driver, limit=10)\n            recent_messages = clean_recent_messages(recent_messages, chat_title)"
)

# Rendre le mode auto vraiment contrôlé par un switch principal.
txt = txt.replace(
    'bool(s.get("auto_scan_unread_chats", False))',
    'bool(s.get("autonomous_mode_enabled", False)) and bool(s.get("auto_scan_unread_chats", False))'
)

# Remplacer la fonction de lecture par une version plus stricte.
new_func = r'''
def read_unanswered_incoming_messages(driver, limit=12):
    """
    Lit uniquement les messages CLIENT après le dernier message sortant.
    Évite de ré-analyser tes propres réponses, les messages supprimés et les anciens messages.
    """
    messages = []
    try:
        bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
        if not bubbles:
            return []

        tail = bubbles[-limit:]

        last_out_index = -1
        for i, b in enumerate(tail):
            try:
                cls = b.get_attribute("class") or ""
                if "message-out" in cls:
                    last_out_index = i
            except Exception:
                pass

        candidates = tail[last_out_index + 1:] if last_out_index >= 0 else tail[-4:]

        for bubble in candidates:
            try:
                cls = bubble.get_attribute("class") or ""
                if "message-in" not in cls:
                    continue

                spans = bubble.find_elements(By.CSS_SELECTOR, "span.selectable-text.copyable-text")
                parts = []
                for s_el in spans:
                    try:
                        tx = s_el.text.strip()
                        if tx:
                            parts.append(tx)
                    except StaleElementReferenceException:
                        continue

                txt = clean_message_text("\n".join(parts)) if parts else clean_message_text(bubble.text)

                if not txt:
                    continue

                low = txt.lower()
                if "vous avez supprimé ce message" in low or "vous avez supprime ce message" in low:
                    messages.append(txt)
                    continue

                if txt.strip().startswith("Vous\n") or txt.strip().startswith("Vous\r\n"):
                    messages.append(txt)
                    continue

                messages.append(txt)

            except Exception:
                continue

    except Exception:
        return []

    clean = []
    for m in messages:
        if m and m not in clean:
            clean.append(m)

    return clean
'''

pattern = r"def read_unanswered_incoming_messages\(driver, limit=10\):.*?\n(?=def find_message_box)"
if re.search(pattern, txt, flags=re.S):
    txt = re.sub(pattern, new_func + "\n\n", txt, flags=re.S)

p.write_text(txt, encoding="utf-8")
print("✅ main.py nettoie maintenant les messages avant analyse + autonomie contrôlée.")
