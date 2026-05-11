from pathlib import Path

p = Path("food_order_guard.py")
txt = p.read_text(encoding="utf-8-sig")

# Ajouter thiep partout où thied/dieb sont reconnus
txt = txt.replace('"riz thied poulet", "riz dieb poulet"', '"riz thied poulet", "riz thiep poulet", "riz dieb poulet"')
txt = txt.replace('"riz thied", "riz dieb"', '"riz thied", "riz thiep", "riz dieb"')
txt = txt.replace('or "thied" in m or "dieb" in m', 'or "thied" in m or "thiep" in m or "dieb" in m')

helper = r'''
def asks_tomorrow_order(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in ["pour demain", "demain", "précommande", "precommande"])

def reply_tomorrow_order(item, zone):
    base = (
        f"D’accord, c’est noté pour demain ✅\n"
        f"{item['label']} — {money(item['price'])}.\n\n"
    )

    if zone and zone.get("fee") is not None:
        total = int(item["price"]) + int(zone["fee"])
        base += (
            f"Livraison {zone['label']} — {money(zone['fee'])}\n"
            f"Total : {money(total)}.\n\n"
        )
    elif zone:
        base += f"Livraison vers {zone['label']} : frais à confirmer selon la distance.\n\n"

    base += (
        "Pour valider la précommande, envoyez votre numéro + l’heure souhaitée + le repère exact."
    )
    return base
'''

if "def asks_tomorrow_order" not in txt:
    txt = txt.replace("def try_food_order_guard", helper + "\n\ndef try_food_order_guard")

old = '''    if item:
        return {
            "reply": reply_order(item, drink, zone),
            "confidence": 0.96,
            "intent": "food_specific_order_total",'''

new = '''    if item:
        if asks_tomorrow_order(combined_message):
            return {
                "reply": reply_tomorrow_order(item, zone),
                "confidence": 0.97,
                "intent": "food_preorder_tomorrow",
                "safe_to_auto_send": True,
                "_state_patch": {
                    "last_category": "food",
                    "last_product_family": "food",
                    "last_product_query": item["label"],
                    "last_food_item": item["id"],
                    "last_food_price": item["price"]
                },
                "_no_media": True,
                "debug": {"source": "food_order_guard", "case": "tomorrow_preorder"}
            }

        return {
            "reply": reply_order(item, drink, zone),
            "confidence": 0.96,
            "intent": "food_specific_order_total",'''

if old in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ food_order_guard.py corrigé pour riz thiep + précommande demain.")
