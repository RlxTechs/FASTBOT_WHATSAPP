from pathlib import Path

p = Path("conversation_brain.py")
txt = p.read_text(encoding="utf-8-sig")

if "from food_order_guard import try_food_order_guard" not in txt:
    txt = txt.replace(
        "from product_sales_engine import try_product_sales_reply",
        "from product_sales_engine import try_product_sales_reply\nfrom food_order_guard import try_food_order_guard"
    )

old = '''    # 1) Nourriture précise en priorité si contexte menu ou message food.
    # Cela évite les erreurs du type “pizza” => iPhone 16.
    food_direct = try_food_sales_reply(message, chat_id)
    if food_direct:
        return food_direct'''

new = '''    # 1) Garde nourriture runtime : commande, zone, délai, quantité, correction.
    food_guard = try_food_order_guard(message, message.split("\\n")[-1], chat_id)
    if food_guard:
        return food_guard

    # 2) Nourriture précise en priorité si contexte menu ou message food.
    food_direct = try_food_sales_reply(message, chat_id)
    if food_direct:
        return food_direct'''

if old in txt:
    txt = txt.replace(old, new)
elif "try_food_order_guard(message" not in txt:
    marker = "    product = try_product_sales_reply(message, chat_id)"
    txt = txt.replace(
        marker,
        '''    food_guard = try_food_order_guard(message, message.split("\\n")[-1], chat_id)
    if food_guard:
        return food_guard

''' + marker
    )

p.write_text(txt, encoding="utf-8")
print("✅ conversation_brain.py branché sur food_order_guard.")
