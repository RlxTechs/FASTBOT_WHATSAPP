from pathlib import Path

p = Path("product_sales_engine.py")
txt = p.read_text(encoding="utf-8-sig")

old = '''def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = normalize(message)'''

new = '''def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = normalize(message)

    # V6.4 : dans une conversation nourriture, ne pas laisser products.json répondre
    # aux messages de délai, validation, suppression ou adresse.
    food_context = (
        state.get("campaign_id") == "menu_food"
        or state.get("campaign_category") == "food"
        or state.get("last_category") == "food"
        or state.get("last_product_family") == "food"
    )

    non_food_keywords = [
        "iphone", "telephone", "téléphone", "ordinateur", "laptop", "pc",
        "imprimante", "cartouche", "tv", "frigo", "refrigerateur",
        "réfrigérateur", "congelateur", "groupe", "stabilisateur",
        "climatiseur", "split", "drone", "drones"
    ]

    blocked_runtime = [
        "dans combien de minutes", "combien de minutes", "combien de temps",
        "ok j ai pris note", "j ai pris note", "vous avez supprime ce message",
        "vous avez supprimé ce message", "mougali", "moungali", "mayanga",
        "bifouiti", "avenue", "adresse"
    ]

    if food_context and any(x in m for x in blocked_runtime):
        return None

    if food_context and not any(x in m for x in non_food_keywords):
        food_words = ["riz", "thieb", "thied", "dieb", "hamburger", "chawarma", "alloco", "poulet", "pizza", "mayo", "livraison"]
        if any(x in m for x in food_words):
            return None'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc try_product_sales_reply non trouvé exactement.")

p.write_text(txt, encoding="utf-8")
print("✅ product_sales_engine.py protégé contre les faux produits en contexte food.")
