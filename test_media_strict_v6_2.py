from media_engine import select_media_for_reply, explain_media_selection

tests = [
    ("Bonjour ! Puis-je en savoir plus à ce sujet ?", {"intent":"seller_fallback_no_context", "reply":"frigos, iPhones, TV"}),
    ("Les iPhone la c'est combien", {"intent":"product_category_iphones_prices", "reply":"Oui les iPhone sont disponibles"}),
    ("Je veux un hamburger", {"intent":"sales_multi_food", "reply":"hamburger disponible"}),
    ("Je veux un frigo", {"intent":"product_from_products_json", "reply":"frigo disponible"}),
    ("Vous avez ordinateur HP ?", {"intent":"product_from_products_json", "reply":"ordinateur disponible"})
]

for msg, result in tests:
    print("="*90)
    print("MSG:", msg)
    print("INTENT:", result["intent"])
    print("SELECTED:", select_media_for_reply(msg, "test_media_strict", result))
    print("TOP DIAG:")
    for r in explain_media_selection(msg, "test_media_strict", result)[:5]:
        print(r.get("id", r.get("type")), r.get("score"), r.get("reasons", r.get("reason")))
