from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

# Importer classify_pre_reply si absent
if "from sales_safety_filters import classify_pre_reply" not in txt:
    txt = txt.replace(
        "from sales_orchestrator import generate_sales_reply",
        "from sales_orchestrator import generate_sales_reply\nfrom sales_safety_filters import classify_pre_reply"
    )

# Importer conversation_brain si absent
if "from conversation_brain import generate_human_sales_reply" not in txt:
    txt = txt.replace(
        "from sales_orchestrator import generate_sales_reply",
        "from sales_orchestrator import generate_sales_reply\nfrom conversation_brain import generate_human_sales_reply"
    )

# Remplacer generate_sales_reply par generate_human_sales_reply
txt = txt.replace(
    "result = generate_sales_reply(combined_msg, chat_id=chat_title)",
    "result = generate_human_sales_reply(combined_msg, chat_id=chat_title)"
)

# Ajouter mémoire conversationnelle si absente
marker = '''reply = result.get("reply", "").strip()
                    conf = float(result.get("confidence", 0))'''

insert = '''# Mémoire conversationnelle : si le cerveau a reconnu un contexte, on le garde.
                    try:
                        state_patch = result.get("_state_patch") or {}
                        if state_patch:
                            set_state(chat_title, state_patch)
                            state.update(state_patch)
                    except Exception as mem_err:
                        print("Erreur mémoire conversation :", repr(mem_err))

                    reply = result.get("reply", "").strip()
                    conf = float(result.get("confidence", 0))'''

if marker in txt and "state_patch = result.get(\"_state_patch\")" not in txt:
    txt = txt.replace(marker, insert)

p.write_text(txt, encoding="utf-8")
print("✅ main.py branché sur conversation_brain + safety_filters.")
