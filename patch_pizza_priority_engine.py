from pathlib import Path

p = Path("autonomous_sales_engine.py")
txt = p.read_text(encoding="utf-8-sig")

if "from pizza_guard import try_pizza_guard" not in txt:
    txt = txt.replace(
        "from typing import Dict, Any",
        "from typing import Dict, Any\nfrom pizza_guard import try_pizza_guard"
    )

old = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:'''

new = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:
    pizza = try_pizza_guard(combined_msg, last_msg, chat_id)
    if pizza:
        return pizza
'''

if old in txt and "pizza = try_pizza_guard" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ autonomous_sales_engine.py : pizza prioritaire branchée.")
