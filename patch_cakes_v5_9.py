from pathlib import Path

p = Path("sales_orchestrator.py")
txt = p.read_text(encoding="utf-8-sig")

# Ajouter détection gâteau si absente
helpers = r'''
def asks_birthday_cake(msg: str) -> bool:
    m = normalize(msg)
    checks = [
        "gateau anniversaire", "gâteau anniversaire", "gateaux anniversaire",
        "gâteaux anniversaire", "gateau d anniversaire", "gâteau d anniversaire",
        "cake anniversaire", "anniversaire"
    ]
    return any(x in m for x in checks)

def birthday_cake_reply() -> str:
    return (
        "Oui, on en fait aussi 🎂✨\n\n"
        "Nous réalisons des gâteaux d’anniversaire sur commande, selon le thème, la taille et votre budget.\n\n"
        "Envoyez-moi simplement :\n"
        "1) le nombre de personnes\n"
        "2) la date prévue\n"
        "3) le thème ou les couleurs\n"
        "4) votre budget si vous en avez un\n\n"
        "Je peux aussi vous montrer quelques modèles pour vous aider à choisir 👇"
    )
'''

if "def asks_birthday_cake" not in txt:
    marker = "def generate_sales_reply(message: str, chat_id: str = \"default\") -> Dict:"
    txt = txt.replace(marker, helpers + "\n" + marker)

# Ajouter priorité gâteau au début de generate_sales_reply
old = '''def generate_sales_reply(message: str, chat_id: str = "default") -> Dict:
    state = get_state(chat_id)'''

new = '''def generate_sales_reply(message: str, chat_id: str = "default") -> Dict:
    state = get_state(chat_id)

    # V5.9 : gâteaux d'anniversaire + images associées
    if asks_birthday_cake(message):
        return {
            "reply": birthday_cake_reply(),
            "confidence": 0.96,
            "intent": "birthday_cakes",
            "safe_to_auto_send": True,
            "debug": {"source": "birthday_cake_sales"}
        }'''

if old in txt and "birthday_cake_sales" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ sales_orchestrator.py patché : gâteaux d'anniversaire.")
