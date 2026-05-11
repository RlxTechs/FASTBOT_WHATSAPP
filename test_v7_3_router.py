from runtime_priority_rules import try_priority_reply
from conversation_brain import generate_human_sales_reply
from bot_core import set_state

chat = "test_v7_3"
set_state(chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food",
    "last_product_family": "food",
    "last_product_query": ""
})

tests = [
    "Et vous avez pas un rendez vous ?",
    "Suis à liberté",
    "Talangaï arrêt liberté",
    "La livraison c'est d'abord combien ?",
    "D’accord à 10h je t’appelle",
    "مرحبًا! هل يمكنني الحصول على مزيد من المعلومات حول هذا؟",
    "En attente de ce message. Vérifiez votre téléphone. En savoir plus",
    "Je confirme la commande le paiement sur place ça fera combien"
]

for msg in tests:
    r = try_priority_reply(msg, msg, chat)
    if not r:
        r = generate_human_sales_reply(msg, chat)

    print("=" * 90)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("SAFE:", r.get("safe_to_auto_send"))
    print("REPONSE:")
    print(r.get("reply"))
