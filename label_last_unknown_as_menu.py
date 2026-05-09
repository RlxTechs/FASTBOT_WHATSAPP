import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
UNKNOWN = BASE / "unknown_campaigns.json"
CAMPAIGNS = BASE / "campaigns.json"
STATE = BASE / "conversations_state.json"

def load(p, d):
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return d

def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

unknown = load(UNKNOWN, {"unknown": {}})
campaigns = load(CAMPAIGNS, {"campaigns": []})
state = load(STATE, {})

waiting = [x for x in unknown.get("unknown", {}).values() if x.get("label_status") == "waiting_label"]
if not waiting:
    print("Aucune carte inconnue à marquer.")
    raise SystemExit

row = waiting[-1]
h = row.get("hash")
chat = row.get("chat_example", "")

camp = None
for c in campaigns.get("campaigns", []):
    if c.get("id") == "menu_food":
        camp = c
        break

if not camp:
    print("Campagne menu_food introuvable.")
    raise SystemExit

camp.setdefault("hashes", [])
if h not in camp["hashes"]:
    camp["hashes"].append(h)

unknown["unknown"][h]["label_status"] = "labeled"
unknown["unknown"][h]["campaign_id"] = "menu_food"
unknown["unknown"][h]["campaign_label"] = camp.get("label", "Pub Menu nourriture")

patch = {
    "needs_campaign_label": False,
    "campaign_id": "menu_food",
    "campaign_label": camp.get("label", "Pub Menu nourriture"),
    "campaign_category": "food",
    "campaign_intent": "food_menu",
    "campaign_product_id": "",
    "campaign_product_query": "menu nourriture",
    "last_category": "food"
}

changed = 0
for chat_id, st in list(state.items()):
    if st.get("unknown_campaign_hash") == h or chat_id == chat:
        st.update(patch)
        st.pop("unknown_campaign_hash", None)
        st.pop("unknown_campaign_source", None)
        st.pop("unknown_campaign_image", None)
        state[chat_id] = st
        changed += 1

save(CAMPAIGNS, campaigns)
save(UNKNOWN, unknown)
save(STATE, state)

print("✅ Dernière carte inconnue marquée comme Pub Menu nourriture.")
print("Hash :", h)
print("Conversation mise à jour :", changed)
