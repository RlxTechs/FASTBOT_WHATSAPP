from bot_core import normalize
from conversation_brain import generate_human_sales_reply
from conversation_guard import clean_recent_messages
from bot_core import set_state

chat = "test_v6_5_pizza"
set_state(chat, {
    "campaign_id": "menu_food",
    "campaign_category": "food",
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    ["𝐏𝐢𝐳𝐳𝐚"],
    ["Poto poto 74 rue mbaka face du consulat du bénin", "𝐏𝐢𝐳𝐳𝐚 🍕"],
    ["Un instant, je vois avec le livreur !", "𝐋𝐚 𝐩𝐢𝐳𝐳𝐚 🍕 𝐜'𝐞𝐬𝐭 𝐛𝐨𝐧 ?"],
    ["Alloco poulet svp", "Et un jus d'orange", "Je suis au quartier bacongo", "D'accord"]
]

print("NORMALIZE:", normalize("𝐏𝐢𝐳𝐳𝐚 🍕"))

for msgs in tests:
    cleaned = clean_recent_messages(msgs, chat)
    print("=" * 90)
    print("RAW:", msgs)
    print("CLEANED:", cleaned)

    if not cleaned:
        print("RESULT: silence")
        continue

    combined = "\\n".join(cleaned)
    r = generate_human_sales_reply(combined, chat)
    print("INTENT:", r.get("intent"))
    print("REPLY:")
    print(r.get("reply"))
