from bot_core import generate_reply, set_state, save_json, STATE_PATH
from smart_reply import generate_smart_reply

CHAT_ID = "test_console"

def clear_context():
    try:
        import json
        if STATE_PATH.exists():
            data = json.loads(STATE_PATH.read_text(encoding="utf-8-sig"))
            data.pop(CHAT_ID, None)
            STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def set_context(name):
    contexts = {
        "menu": {
            "campaign_id": "menu_food",
            "campaign_label": "Pub Menu nourriture",
            "campaign_category": "food",
            "campaign_intent": "food_menu",
            "last_category": "food"
        },
        "tv": {
            "campaign_id": "tv_smart",
            "campaign_label": "Pub TV Smart",
            "campaign_category": "tv",
            "campaign_intent": "product_category",
            "last_category": "tv"
        },
        "groupe": {
            "campaign_id": "groupes_electrogenes",
            "campaign_label": "Pub Groupes électrogènes",
            "campaign_category": "energie",
            "campaign_intent": "product",
            "campaign_product_id": "groupe-electrogene",
            "campaign_product_query": "groupe electrogene",
            "last_category": "energie",
            "last_product_id": "groupe-electrogene"
        },
        "frigo": {
            "campaign_id": "electromenager_frigo",
            "campaign_label": "Pub Réfrigérateurs",
            "campaign_category": "refrigerateur",
            "campaign_intent": "product_category",
            "campaign_product_id": "west-pool-frigo",
            "campaign_product_query": "refrigerateur",
            "last_category": "refrigerateur",
            "last_product_id": "west-pool-frigo"
        },
        "congelateur": {
            "campaign_id": "electromenager_congelateur",
            "campaign_label": "Pub Congélateurs",
            "campaign_category": "congelateur",
            "campaign_intent": "product_category",
            "campaign_product_id": "congelo-pic",
            "campaign_product_query": "congelateur",
            "last_category": "congelateur",
            "last_product_id": "congelo-pic"
        },
        "split": {
            "campaign_id": "electromenager_split",
            "campaign_label": "Pub Climatiseurs / Split",
            "campaign_category": "split",
            "campaign_intent": "product_category",
            "campaign_product_id": "nasco-clim",
            "campaign_product_query": "climatiseur split",
            "last_category": "split",
            "last_product_id": "nasco-clim"
        }
    }

    if name not in contexts:
        print("Contextes disponibles :", ", ".join(contexts.keys()))
        return

    set_state(CHAT_ID, contexts[name])
    print(f"✅ Contexte défini : {contexts[name]['campaign_label']}")

print("Test cerveau bot V4.")
print("Commandes :")
print("/context menu | /context tv | /context groupe | /context frigo | /context congelateur | /context split")
print("/clear = effacer contexte")
print("Exemple : /context menu puis tape : prix ?")
print("Tape exit pour quitter.\n")

while True:
    msg = input("Client > ").strip()

    if msg.lower() in {"exit", "quit", "q"}:
        break

    if msg.startswith("/context"):
        parts = msg.split(maxsplit=1)
        if len(parts) == 2:
            set_context(parts[1].strip().lower())
        else:
            print("Exemple : /context menu")
        continue

    if msg == "/clear":
        clear_context()
        print("✅ Contexte effacé.")
        continue

    result = generate_smart_reply(msg, chat_id=CHAT_ID)
    print("\nIntent :", result["intent"])
    print("Confiance :", result["confidence"])
    print("Auto-safe :", result["safe_to_auto_send"])
    print("Réponse :")
    print(result["reply"])
    print("-" * 60)
