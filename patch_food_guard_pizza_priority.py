from pathlib import Path

p = Path("food_order_guard.py")
txt = p.read_text(encoding="utf-8-sig")

if "from pizza_guard import try_pizza_guard" not in txt:
    txt = txt.replace(
        "from bot_core import normalize, get_state",
        "from bot_core import normalize, get_state\nfrom pizza_guard import try_pizza_guard"
    )

old = '''def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:'''

new = '''def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    pizza = try_pizza_guard(combined_message, latest_message, chat_id)
    if pizza:
        return pizza
'''

if old in txt and "pizza = try_pizza_guard" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ food_order_guard.py : pizza prioritaire branchée aussi.")
