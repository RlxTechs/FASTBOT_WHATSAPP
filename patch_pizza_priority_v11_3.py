from pathlib import Path

p = Path("autonomous_sales_engine.py")
txt = p.read_text(encoding="utf-8-sig")

if "from pizza_guard import try_pizza_guard" not in txt:
    txt = txt.replace(
        "from typing import Dict, Any",
        "from typing import Dict, Any\nfrom pizza_guard import try_pizza_guard"
    )

if "pizza = try_pizza_guard(combined_msg, last_msg, chat_id)" not in txt:
    marker = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:'''
    txt = txt.replace(
        marker,
        marker + '''
    pizza = try_pizza_guard(combined_msg, last_msg, chat_id)
    if pizza:
        return pizza
'''
    )

p.write_text(txt, encoding="utf-8")
print("✅ Priorité pizza vérifiée dans autonomous_sales_engine.py.")
