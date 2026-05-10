from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

# Importer le nouveau cerveau
if "from conversation_brain import generate_human_sales_reply" not in txt:
    txt = txt.replace(
        "from sales_orchestrator import generate_sales_reply",
        "from sales_orchestrator import generate_sales_reply\nfrom conversation_brain import generate_human_sales_reply"
    )

# Remplacer l'appel final
txt = txt.replace(
"result = generate_sales_reply(combined_msg, chat_id=chat_title)",
"result = generate_human_sales_reply(combined_msg, chat_id=chat_title)"
)

# Appliquer automatiquement le _state_patch après génération de la réponse
marker = '''reply = result.get("reply", "").strip()
                    conf = float(result.get("confidence", 0))'''

insert = '''# Appliquer mémoire conversationnelle si le cerveau a reconnu un contexte.
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
print("✅ main.py branché sur conversation_brain + mémoire.")
