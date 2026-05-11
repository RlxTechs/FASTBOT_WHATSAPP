from pathlib import Path

p = Path("conversation_brain.py")
txt = p.read_text(encoding="utf-8-sig")

if "from runtime_priority_rules import try_priority_reply" not in txt:
    txt = txt.replace(
        "from bot_core import normalize, get_state",
        "from bot_core import normalize, get_state\nfrom runtime_priority_rules import try_priority_reply"
    )

old = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)'''

new = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)

    priority_direct = try_priority_reply(message, message.split("\\n")[-1], chat_id)
    if priority_direct:
        return priority_direct'''

if old in txt and "priority_direct = try_priority_reply" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ conversation_brain.py utilise aussi le router prioritaire.")
