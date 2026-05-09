from sales_orchestrator import generate_sales_reply
from bot_core import set_state

tests = [
    ("food", "Vous êtes dans quel quartier ?"),
    ("tech", "Vous êtes dans quel quartier ?"),
    ("energie", "Vous êtes dans quel quartier ?"),
    ("none", "Vous êtes dans quel quartier ?"),
    ("none", "ordinateur HP vous êtes dans quel quartier ?"),
    ("none", "groupe électrogène vous êtes dans quel quartier ?"),
]

for ctx, msg in tests:
    chat = "test_addr_" + ctx

    if ctx == "food":
        set_state(chat, {"campaign_id":"menu_food","campaign_category":"food","last_category":"food"})
    elif ctx == "tech":
        set_state(chat, {"campaign_id":"laptop_hp","campaign_category":"tech","last_category":"tech"})
    elif ctx == "energie":
        set_state(chat, {"campaign_id":"groupes_electrogenes","campaign_category":"energie","last_category":"energie"})
    else:
        set_state(chat, {})

    r = generate_sales_reply(msg, chat)
    print("="*70)
    print("CONTEXTE:", ctx)
    print("CLIENT:", msg)
    print("INTENT:", r.get("intent"))
    print("REPONSE:")
    print(r.get("reply"))
