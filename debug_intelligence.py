import json
from pathlib import Path

from bot_core import set_state, STATE_PATH
from smart_reply import generate_smart_reply
from intent_bank import explain_match

CHAT = "debug_intelligence"

def reset_state():
    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8-sig"))
            data.pop(CHAT, None)
            STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

def set_context(name):
    contexts = {
        "menu": {
            "campaign_id": "menu_food",
            "campaign_label": "Pub Menu nourriture",
            "campaign_category": "food",
            "campaign_intent": "food_menu",
            "last_category": "food"
        },
        "groupe": {
            "campaign_id": "groupes_electrogenes",
            "campaign_label": "Pub Groupes électrogènes",
            "campaign_category": "energie",
            "campaign_product_id": "groupe-electrogene",
            "campaign_product_query": "groupe electrogene",
            "last_category": "energie",
            "last_product_id": "groupe-electrogene"
        },
        "tv": {
            "campaign_id": "tv_smart",
            "campaign_label": "Pub TV Smart",
            "campaign_category": "tv",
            "campaign_product_query": "tv smart",
            "last_category": "tv"
        }
    }
    set_state(CHAT, contexts[name])

tests = [
    ("none", "Bonjour ! Puis-je en savoir plus à ce sujet ?"),
    ("menu", "Bonjour ! Puis-je en savoir plus à ce sujet ?"),
    ("menu", "prix ?"),
    ("menu", "menu"),
    ("groupe", "combien ?"),
    ("tv", "32 pouces"),
    ("none", "dernier prix ?"),
    ("none", "c'est négociable ?"),
    ("none", "vous faites la livraison ?"),
    ("none", "je suis à Moungali"),
    ("none", "garantie combien ?"),
    ("none", "c'est neuf ou occasion ?"),
    ("none", "envoyez photo réelle"),
    ("none", "comment payer ?"),
    ("none", "je veux commander"),
    ("none", "vous êtes où ?"),
    ("none", "vous êtes ouverts ?"),
    ("none", "je veux parler à un conseiller"),
    ("none", "ça ne marche pas"),
    ("none", "prix de gros ?"),
    ("none", "lequel est mieux ?"),
    ("none", "blabla test inconnu 987")
]

print("=" * 80)
print("DEBUGGER INTELLIGENCE V4.3")
print("=" * 80)

for ctx, msg in tests:
    reset_state()
    if ctx != "none":
        set_context(ctx)

    print("\nCLIENT :", msg)
    print("CONTEXTE :", ctx)

    bank = explain_match(msg)
    print("BANQUE MATCH :")
    print(json.dumps(bank, ensure_ascii=False, indent=2)[:1600])

    result = generate_smart_reply(msg, chat_id=CHAT)
    print("\nRÉSULTAT FINAL :")
    print("Intent :", result.get("intent"))
    print("Confiance :", result.get("confidence"))
    print("Safe :", result.get("safe_to_auto_send"))
    print("Réponse :")
    print(result.get("reply"))
    print("-" * 80)

print("\n✅ Debug terminé.")
print("Fichiers utiles : unknown_messages.jsonl, unknown_messages_index.json, debug_logs.jsonl")
