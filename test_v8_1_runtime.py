from bot_core import set_state
from sales_director import try_sales_director
from autonomous_sales_engine import decide_reply

chat = "test_v8_1"

set_state(chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    "Bonjour ! Puis-je en savoir plus à ce sujet ?",
    "Suis à liberté",
    "Talangaï arrêt liberté",
    "La livraison c'est d'abord combien ?",
    "Et vous avez pas un rendez vous ?",
    "Vous pouvez arriver dans combien de temps ?",
    "Veuillez ramener la différence aussi, j'ai 10.000frs sur moi",
    "OK",
    "Je confirme"
]

for msg in tests:
    r = decide_reply(msg, msg, chat)
    print("=" * 90)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("CONF:", r.get("confidence"))
    print("RÉPONSE:")
    print(r.get("reply"))
