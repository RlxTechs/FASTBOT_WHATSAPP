from pathlib import Path

p = Path("product_sales_engine.py")
txt = p.read_text(encoding="utf-8-sig")

old = '''def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = normalize(message)'''

new = '''def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = normalize(message)

    # V7.3 : bloquer products.json sur les phrases qui ne sont pas des produits.
    absolute_block = [
        "rendez vous", "rendez-vous", "rdv",
        "livraison", "frais", "combien de temps", "combien de minutes",
        "adresse", "situé", "situe", "où", "ou", "paiement", "payer",
        "sur place", "je t appelle", "je t’appelle", "ok", "d accord", "d’accord"
    ]

    product_keywords = [
        "iphone", "telephone", "téléphone", "ordinateur", "laptop", "pc",
        "imprimante", "cartouche", "tv", "frigo", "refrigerateur",
        "réfrigérateur", "congelateur", "groupe", "stabilisateur",
        "climatiseur", "split", "drone", "pack office", "windows"
    ]

    food_context = (
        state.get("campaign_id") == "menu_food"
        or state.get("campaign_category") == "food"
        or state.get("last_category") == "food"
        or state.get("last_product_family") in {"food", "pizza"}
    )

    if any(x in m for x in absolute_block) and not any(x in m for x in product_keywords):
        return None

    if food_context and not any(x in m for x in product_keywords):
        food_words = [
            "riz", "thieb", "thiep", "dieb", "hamburger", "chawarma",
            "alloco", "poulet", "pizza", "mayo", "livraison", "rendez"
        ]
        if any(x in m for x in food_words):
            return None'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc try_product_sales_reply non trouvé exactement.")

p.write_text(txt, encoding="utf-8")
print("✅ product_sales_engine.py protégé V7.3.")
