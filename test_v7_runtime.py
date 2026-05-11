from conversation_guard import clean_recent_messages
from conversation_brain import generate_human_sales_reply
from sales_safety_filters import classify_pre_reply
from bot_core import set_state

chat = "test_v7_food"
set_state(chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    ["Bonjour", "Alloco + poulet c'est disponible.?", "Appel vocal manqué\nRappelez des personnes sur votre téléphone"],
    ["Alloco poulet svp", "Et un jus d'orange", "Je suis au quartier bacongo"],
    ["Alloco poulet svp", "Et un jus d'orange", "Je suis au quartier bacongo", "D'accord"],
    ["Riz thied poulet", "Mougali Avenue Sergent Malamine", "Dans combien de minutes"],
    ["Vous\nok, ca fera 3000f\nOui", "Vous avez supprimé ce message"],
    ["Je peux faire la commande ?", "Je vous écris pour ça", "Vous allez faire la livraison vers la morgue"],
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
