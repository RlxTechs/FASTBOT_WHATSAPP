from pathlib import Path

p = Path("conversation_brain.py")
txt = p.read_text(encoding="utf-8-sig")

if "from manual_approval import consume_decision" not in txt:
    txt = txt.replace(
        "from product_sales_engine import try_product_sales_reply",
        "from product_sales_engine import try_product_sales_reply\nfrom manual_approval import consume_decision"
    )

old = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)'''

new = '''def generate_human_sales_reply(message: str, chat_id: str = "default") -> Dict[str, Any]:
    state = get_state(chat_id)

    # V6.5 : si toi/admin as pris une décision manuelle, on l’envoie en priorité.
    operator_decision = consume_decision(chat_id)
    if operator_decision:
        return operator_decision'''

if old in txt and "operator_decision = consume_decision(chat_id)" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("✅ conversation_brain.py : décisions admin prioritaires.")
