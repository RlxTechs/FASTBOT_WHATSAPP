from pathlib import Path

p = Path("conversation_brain.py")
txt = p.read_text(encoding="utf-8-sig")

if "from food_sales_engine import try_food_sales_reply" not in txt:
    txt = txt.replace(
        "from product_sales_engine import try_product_sales_reply",
        "from product_sales_engine import try_product_sales_reply\nfrom food_sales_engine import try_food_sales_reply"
    )

old = '''    # 1) Produits officiels products.json en priorité : iPhone, XR, 12 Pro Max, imprimante, laptop, TV...
    product = try_product_sales_reply(message, chat_id)
    if product:
        return product'''

new = '''    # 1) Nourriture précise en priorité si contexte menu ou message food.
    # Cela évite les erreurs du type “pizza” => iPhone 16.
    food_direct = try_food_sales_reply(message, chat_id)
    if food_direct:
        return food_direct

    # 2) Produits officiels products.json : iPhone, XR, 12 Pro Max, imprimante, laptop, TV...
    product = try_product_sales_reply(message, chat_id)
    if product:
        return product'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc priorité produit non trouvé exactement. On vérifie manuellement si besoin.")

p.write_text(txt, encoding="utf-8")
print("✅ conversation_brain.py : food direct avant products.json.")
