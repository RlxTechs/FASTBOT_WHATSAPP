from autonomous_sales_engine import decide_reply
from lead_memory import update_lead, remember_outgoing

chat = "test_pizza_v11_3"

update_lead(chat, {
    "last_outgoing_text": "",
    "stage": "new"
})

tests = [
    "Bonsoir les pizzas c'est a combien ?",
    "Pizza 🍕",
    "𝐏𝐢𝐳𝐳𝐚",
    "Dürum poulet c'est combien ?"
]

for msg in tests:
    r = decide_reply(msg, msg, chat)
    print("=" * 90)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("REPLY:")
    print(r.get("reply"))

remember_outgoing(
    chat,
    "Bonjour 👋 Voici notre menu disponible aujourd’hui 🍽️\nAlloco poulet — 2.000 F\nPortion de frites — 1.000 F",
    "food_menu_sent",
    True
)

r = decide_reply("Bonsoir les pizzas c'est a combien ?", "Bonsoir les pizzas c'est a combien ?", chat)
print("=" * 90)
print("CAS MENU STANDARD DEJA ENVOYE")
print("INTENT:", r.get("intent"))
print("REPLY:")
print(r.get("reply"))
