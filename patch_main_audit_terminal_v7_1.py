from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

txt = txt.replace(
    "from message_audit import audit_chat_messages",
    "from message_audit import audit_chat_messages, print_audit_rows"
)

old = '''if bool(s.get("audit_all_visible_messages", True)):
                audit_chat_messages(driver, chat_title)'''

new = '''if bool(s.get("audit_all_visible_messages", True)):
                audit_rows = audit_chat_messages(driver, chat_title)
                print_audit_rows(audit_rows)'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc audit non trouvé exactement. Vérifie main.py.")

p.write_text(txt, encoding="utf-8")
print("✅ main.py affiche maintenant l'audit complet dans le terminal.")
