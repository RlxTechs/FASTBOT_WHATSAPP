import json
from pathlib import Path

from bot_core import set_state, STATE_PATH
from sales_orchestrator import generate_sales_reply

CHAT = "debug_v5_3"

def reset():
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text(encoding="utf-8-sig"))
        data.pop(CHAT, None)
        STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def context_food():
    set_state(CHAT, {
        "needs_campaign_label": False,
        "campaign_id": "menu_food",
        "campaign_label": "Pub Menu nourriture",
        "campaign_category": "food",
        "last_category": "food"
    })

tests = [
    ("food", "Vous êtes à pointe noire ?\nVous avez quoi là-bas vous pouvez me montrer ce que vous faites envoyez-moi ça s'il vous plaît\nBsr Hamburger c'est disponible"),
    ("none", "Vous avez quoi là-bas vous pouvez me montrer ce que vous faites envoyez-moi ça s'il vous plaît"),
    ("food", "Bsr Hamburger c'est disponible"),
    ("food", "vous êtes dans quelle ville ?"),
    ("none", "Vous êtes à pointe noire ?")
]

for ctx, msg in tests:
    reset()
    if ctx == "food":
        context_food()

    r = generate_sales_reply(msg, CHAT)

    print("=" * 80)
    print("CONTEXTE :", ctx)
    print("MESSAGE :")
    print(msg)
    print("INTENT :", r.get("intent"))
    print("CONF :", r.get("confidence"))
    print("RÉPONSE :")
    print(r.get("reply"))
