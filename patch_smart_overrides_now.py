from pathlib import Path

p = Path("autonomous_sales_engine.py")
txt = p.read_text(encoding="utf-8-sig")

if "from smart_overrides import try_smart_override" not in txt:
    txt = txt.replace(
        "from typing import Dict, Any",
        "from typing import Dict, Any\nfrom smart_overrides import try_smart_override"
    )

old = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:
    pre = classify_pre_reply(combined_msg, last_msg, chat_id)
    if pre:
        return pre'''

new = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:
    smart = try_smart_override(combined_msg, last_msg, chat_id)
    if smart:
        return smart

    pre = classify_pre_reply(combined_msg, last_msg, chat_id)
    if pre:
        return pre'''

if old in txt:
    txt = txt.replace(old, new)
elif "smart = try_smart_override" not in txt:
    marker = '''def decide_reply(combined_msg: str, last_msg: str, chat_id: str = "default") -> Dict[str, Any]:'''
    txt = txt.replace(
        marker,
        marker + '''
    smart = try_smart_override(combined_msg, last_msg, chat_id)
    if smart:
        return smart
'''
    )

p.write_text(txt, encoding="utf-8")
print("✅ autonomous_sales_engine.py corrigé.")
