from sales_orchestrator import generate_sales_reply
from bot_core import set_state

CHAT = "test_v5_5"

set_state(CHAT, {
    "needs_campaign_label": False,
    "campaign_id": "menu_food",
    "campaign_label": "Pub Menu nourriture",
    "campaign_category": "food",
    "last_category": "food"
})

tests = [
    "Heure de fermeture ?",
    "Vous livrez à Pointe-Noire ?",
    "Je suis à pointe noire",
    "Bsr Hamburger c'est disponible"
]

for t in tests:
    r = generate_sales_reply(t, CHAT)
    print("="*70)
    print("CLIENT:", t)
    print("INTENT:", r.get("intent"))
    print("REPONSE:")
    print(r.get("reply"))
