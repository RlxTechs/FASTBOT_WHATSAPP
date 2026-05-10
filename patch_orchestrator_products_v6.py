from pathlib import Path

p = Path("sales_orchestrator.py")
txt = p.read_text(encoding="utf-8-sig")

if "from product_sales_engine import try_product_sales_reply" not in txt:
    txt = txt.replace(
        "from smart_reply import generate_smart_reply",
        "from smart_reply import generate_smart_reply\nfrom product_sales_engine import try_product_sales_reply"
    )

needle = '''    # 7) Sinon, utiliser le cerveau actuel.
    return generate_smart_reply(message, chat_id=chat_id)'''

patch = '''    # 7) Produits officiels depuis products.json : prix + images cohérents avec le site.
    product_result = try_product_sales_reply(message, chat_id=chat_id)
    if product_result:
        return product_result

    # 8) Sinon, utiliser le cerveau actuel.
    return generate_smart_reply(message, chat_id=chat_id)'''

if needle in txt:
    txt = txt.replace(needle, patch)
elif "try_product_sales_reply(message" not in txt:
    print("⚠️ Bloc final non trouvé. On ajoute une sécurité simple en fin de fonction si nécessaire.")

p.write_text(txt, encoding="utf-8")
print("✅ sales_orchestrator.py relié à products.json.")
