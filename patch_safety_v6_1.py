from pathlib import Path

p = Path("sales_safety_filters.py")
txt = p.read_text(encoding="utf-8-sig")

txt = txt.replace(
'''def is_ack_only(message: str) -> bool:
    m = normalize(message)''',
'''def is_ack_only(message: str) -> bool:
    m = normalize(message)'''
)

# Ajouter svp/stp dans les mots silencieux
txt = txt.replace(
'''"cool"
    }''',
'''"cool",
        "svp",
        "stp",
        "s il vous plait",
        "s'il vous plait",
        "s il vous plaît",
        "s'il vous plaît",
        "sil vous plait",
        "sil vous plaît"
    }'''
)

txt = txt.replace(
'''    allowed_words = {
        "d", "accord", "daccord", "ok", "merci", "beaucoup", "bien",
        "recu", "reçu", "note", "noté", "parfait", "cool", "marche", "ca", "ça"
    }''',
'''    allowed_words = {
        "d", "accord", "daccord", "ok", "merci", "beaucoup", "bien",
        "recu", "reçu", "note", "noté", "parfait", "cool", "marche", "ca", "ça",
        "svp", "stp", "s", "il", "vous", "plait", "plaît"
    }'''
)

# Corriger classify_pre_reply pour ne pas bloquer quand combined contient une vraie question avant le “svp”.
old = '''def classify_pre_reply(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict]:
    # 1) Si le dernier message est juste un accusé de réception, on ne répond pas.
    if is_ack_only(latest_message):
        return {
            "reply": "",
            "confidence": 0.0,
            "intent": "no_reply_acknowledgement",
            "safe_to_auto_send": False,
            "debug": {
                "source": "sales_safety_filters",
                "reason": "latest message is acknowledgement only",
                "latest_message": latest_message
            }
        }'''

new = '''def classify_pre_reply(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict]:
    # 1) Si le dernier message est juste un accusé de réception, on ne répond pas.
    # Mais si combined_message contient une vraie question avant “svp”, on laisse le cerveau répondre.
    combined_norm = normalize(combined_message)
    latest_norm = normalize(latest_message)
    only_latest = combined_norm == latest_norm

    if only_latest and is_ack_only(latest_message):
        return {
            "reply": "",
            "confidence": 0.0,
            "intent": "no_reply_acknowledgement",
            "safe_to_auto_send": False,
            "debug": {
                "source": "sales_safety_filters",
                "reason": "latest message is acknowledgement/polite filler only",
                "latest_message": latest_message
            }
        }'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("Bloc classify_pre_reply non trouvé exactement, vérification manuelle si besoin.")

p.write_text(txt, encoding="utf-8")
print("✅ sales_safety_filters.py corrigé.")
