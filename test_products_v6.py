from product_sales_engine import try_product_sales_reply

tests = [
    "Les iPhone la c'est combien",
    "iPhone 13 Pro Max combien ?",
    "Vous avez imprimante Epson ?",
    "Je veux une imprimante L3252",
    "Core i3 combien ?",
    "TV LG 32 pouces prix ?"
]

for t in tests:
    r = try_product_sales_reply(t, "test_products")
    print("=" * 90)
    print("CLIENT:", t)
    if not r:
        print("AUCUNE REPONSE PRODUIT")
        continue
    print("INTENT:", r.get("intent"))
    print("CONF:", r.get("confidence"))
    print("REPONSE:")
    print(r.get("reply"))
    print("IMAGES:", r.get("_media_images"))
