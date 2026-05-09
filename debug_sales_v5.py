import json
from pathlib import Path

from bot_core import set_state, STATE_PATH
from smart_reply import generate_smart_reply

CHAT = "debug_sales_v5"

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
            "needs_campaign_label": False,
            "campaign_id": "menu_food",
            "campaign_label": "Pub Menu nourriture",
            "campaign_category": "food",
            "campaign_intent": "food_menu",
            "last_category": "food"
        },
        "tv": {
            "needs_campaign_label": False,
            "campaign_id": "tv_smart",
            "campaign_label": "Pub TV Smart",
            "campaign_category": "tv",
            "campaign_product_query": "tv smart",
            "last_category": "tv"
        },
        "groupe": {
            "needs_campaign_label": False,
            "campaign_id": "groupes_electrogenes",
            "campaign_label": "Pub Groupes électrogènes",
            "campaign_category": "energie",
            "campaign_product_id": "groupe-electrogene",
            "campaign_product_query": "groupe electrogene",
            "last_category": "energie",
            "last_product_id": "groupe-electrogene"
        },
        "frigo": {
            "needs_campaign_label": False,
            "campaign_id": "electromenager_frigo",
            "campaign_label": "Pub Réfrigérateurs",
            "campaign_category": "refrigerateur",
            "campaign_product_id": "west-pool-frigo",
            "campaign_product_query": "refrigerateur",
            "last_category": "refrigerateur",
            "last_product_id": "west-pool-frigo"
        }
    }

    set_state(CHAT, contexts[name])

tests = [
    ("menu", "Bonjour ! Puis-je en savoir plus à ce sujet ?"),
    ("menu", "vous êtes dans quelle ville ?"),
    ("menu", "restaurant où ?"),
    ("menu", "livraison combien ?"),
    ("menu", "prix ?"),
    ("menu", "je veux commander"),
    ("tv", "Bonjour ! Puis-je en savoir plus à ce sujet ?"),
    ("tv", "32 pouces"),
    ("tv", "vous êtes dans quelle ville ?"),
    ("groupe", "combien ?"),
    ("groupe", "5 kva"),
    ("frigo", "vous livrez ?"),
    ("none", "vous êtes où ?"),
    ("none", "dernier prix ?"),
    ("none", "garantie combien ?"),
    ("none", "c'est neuf ou occasion ?"),
    ("none", "je veux commander")
]

print("=" * 90)
print("DEBUG SALES V5")
print("=" * 90)

for ctx, msg in tests:
    reset_state()
    if ctx != "none":
        set_context(ctx)

    result = generate_smart_reply(msg, chat_id=CHAT)

    print("\nCONTEXTE :", ctx)
    print("CLIENT :", msg)
    print("INTENT :", result.get("intent"))
    print("CONFIANCE :", result.get("confidence"))
    print("SAFE :", result.get("safe_to_auto_send"))
    print("RÉPONSE :")
    print(result.get("reply"))
    print("-" * 90)

print("\n✅ Debug terminé.")
