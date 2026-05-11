from conversation_guard import clean_recent_messages
from conversation_brain import generate_human_sales_reply
from sales_safety_filters import classify_pre_reply
from bot_core import set_state

chat = "test_v6_4_food"
set_state(chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    ["Bonjour ! Puis-je en savoir plus à ce sujet ?", "Mayanga...", "Ok j'ai pris note..."],
    ["Riz thied poulet", "Mougali Avenue Sergent Malamine"],
    ["Riz thied poulet", "Mougali Avenue Sergent Malamine", "Dans combien de minutes"],
    ["Vous\nok, ca fera 3000f\nOui", "Dans combien de minutes"],
    ["Vous avez supprimé ce message"],
    ["Ya poulet mayo"],
    ["La pizza vous la faite à combien ??"],
    ["1 x"]
]

for msgs in tests:
    cleaned = clean_recent_messages(msgs, chat)
    print("=" * 90)
    print("RAW:", msgs)
    print("CLEAN:", cleaned)

    if not cleaned:
        print("RESULT: silence")
        continue

    combined = "\n".join(cleaned)
    latest = cleaned[-1]

    pre = classify_pre_reply(combined, latest, chat)
    r = pre if pre else generate_human_sales_reply(combined, chat)

    print("INTENT:", r.get("intent"))
    print("REPLY:")
    print(r.get("reply"))
