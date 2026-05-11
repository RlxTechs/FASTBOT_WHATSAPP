from conversation_brain import generate_human_sales_reply
from sales_safety_filters import classify_pre_reply
from bot_core import set_state

food_chat = "test_food_v6_3"
set_state(food_chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food"
})

tests = [
    ("noctx", "Cc"),
    ("food", "Transféré"),
    ("food", "Possible de me livrer le riz dieb 2500 f je suis à bifouiti en face de la gendarmerie"),
    ("food", "La pizza vous la faite à combien ??"),
    ("food", "Bonjour ! Puis-je en savoir plus à ce sujet ?"),
    ("food", "Je veux un hamburger"),
]

for ctx, msg in tests:
    chat = food_chat if ctx == "food" else "test_noctx_v6_3"

    pre = classify_pre_reply(msg, msg, chat)
    if pre:
        r = pre
    else:
        r = generate_human_sales_reply(msg, chat)

    print("=" * 90)
    print("CTX:", ctx)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("CONF:", r.get("confidence"))
    print("REPLY:")
    print(r.get("reply"))
