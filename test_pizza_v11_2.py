from autonomous_sales_engine import decide_reply
from lead_memory import update_lead, remember_outgoing

chat = "test_pizza_v11_2"

# Cas 1 : client demande pizza sans menu déjà envoyé
update_lead(chat, {
    "last_outgoing_text": "",
    "stage": "new"
})

tests = [
    "Bonsoir les pizzas c'est a combien ?",
    "𝐏𝐢𝐳𝐳𝐚",
    "Pizza 🍕",
]

for msg in tests:
    r = decide_reply(msg, msg, chat)
    print("=" * 90)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("CONF:", r.get("confidence"))
    print("REPLY:")
    print(r.get("reply"))

# Cas 2 : menu standard déjà envoyé, donc seulement menu pizza
remember_outgoing(chat, "Bonjour 👋 Voici notre menu disponible aujourd’hui 🍽️\nAlloco poulet — 2.000 F\nPortion de frites — 1.000 F", "food_menu_sent", True)

r = decide_reply("Bonsoir les pizzas c'est a combien ?", "Bonsoir les pizzas c'est a combien ?", chat)
print("=" * 90)
print("CAS MENU STANDARD DEJA ENVOYE")
print("INTENT:", r.get("intent"))
print("REPLY:")
print(r.get("reply"))
