from pathlib import Path

p = Path("conversation_brain.py")
txt = p.read_text(encoding="utf-8-sig")

helper = r'''
def asks_about_deleted_messages(message: str) -> bool:
    m = normalize(message)
    checks = [
        "pourquoi vous supprimez",
        "pourquoi vous supprimer",
        "vous supprimez les messages",
        "vous avez supprime",
        "vous avez supprimé",
        "messages supprimes",
        "messages supprimés"
    ]
    return any(x in m for x in checks)

def deleted_message_apology_reply() -> str:
    return (
        "Désolé pour la confusion 🙏\n"
        "Il y a eu une erreur de réponse, donc le message a été supprimé pour éviter de vous induire en erreur.\n\n"
        "On reprend clairement : dites-moi le plat voulu + votre quartier + votre numéro, "
        "et je vous confirme le total exact avant validation."
    )
'''

if "def asks_about_deleted_messages" not in txt:
    txt = txt.replace("def generate_human_sales_reply", helper + "\n\ndef generate_human_sales_reply")

old = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)'''

new = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)

    # V7.1 : si le client remarque une suppression, on s'excuse clairement.
    if asks_about_deleted_messages(message):
        return {
            "reply": deleted_message_apology_reply(),
            "confidence": 0.97,
            "intent": "deleted_message_apology",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "conversation_brain", "case": "deleted_message_complaint"}
        }'''

if old in txt and "deleted_message_apology" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ conversation_brain.py corrigé pour plaintes sur messages supprimés.")
