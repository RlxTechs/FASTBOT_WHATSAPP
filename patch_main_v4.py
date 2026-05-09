from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

txt = txt.replace(
    "from bot_core import generate_reply",
    "from smart_reply import generate_smart_reply\nfrom bot_core import get_state, set_state\nfrom campaign_context import detect_campaign_from_chat"
)

old = "result = generate_reply(last_msg, chat_id=chat_title)"
new = """try:
                        state = get_state(chat_title)
                        if not state.get("campaign_id"):
                            camp = detect_campaign_from_chat(driver, chat_title)
                            if camp:
                                set_state(chat_title, camp.get("state_patch", {}))
                                print("Contexte pub détecté :", camp.get("label"), "| source :", camp.get("source"))
                    except Exception as ctx_err:
                        print("Contexte pub non détecté :", repr(ctx_err))

                    result = generate_smart_reply(last_msg, chat_id=chat_title)"""

if old not in txt:
    print("⚠️ Patch main.py : ancienne ligne non trouvée. Vérifie main.py manuellement.")
else:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("main.py patché pour V4")
