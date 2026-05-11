from conversation_brain import generate_human_sales_reply
from food_order_guard import try_food_order_guard
from bot_core import set_state

chat = "test_v7_1"
set_state(chat, {
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    "Pourquoi vous supprimez les messages je peux payer aujourd’hui si vous voulez",
    "Riz thiep pour demain",
    "Tout proche de la morgue de CHU",
]

for msg in tests:
    print("=" * 90)
    print("CLIENT:", msg)
    r = generate_human_sales_reply(msg, chat)
    print("INTENT:", r.get("intent"))
    print("REPONSE:")
    print(r.get("reply"))
