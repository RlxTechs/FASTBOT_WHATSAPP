from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from smart_reply import generate_smart_reply" not in txt:
    txt = txt.replace(
        "from bot_core import generate_reply",
        "from smart_reply import generate_smart_reply\nfrom bot_core import get_state, set_state\nfrom campaign_context import detect_campaign_from_chat"
    )

if "detect_campaign_from_chat(driver, chat_title)" not in txt:
    old1 = "result = generate_reply(last_msg, chat_id=chat_title)"
    old2 = "result = generate_smart_reply(last_msg, chat_id=chat_title)"

    block = """try:
                        state = get_state(chat_title)
                        if not state.get("campaign_id"):
                            camp = detect_campaign_from_chat(driver, chat_title)
                            if camp:
                                if camp.get("unknown"):
                                    print("Pub Facebook inconnue enregistrée :", camp.get("hash"))
                                    print("Va dans campaign_captures puis lance campaign_admin.bat pour l'étiqueter.")
                                else:
                                    set_state(chat_title, camp.get("state_patch", {}))
                                    print("Contexte pub détecté :", camp.get("label"), "| source :", camp.get("source"))
                    except Exception as ctx_err:
                        print("Contexte pub non détecté :", repr(ctx_err))

                    result = generate_smart_reply(last_msg, chat_id=chat_title)"""

    if old1 in txt:
        txt = txt.replace(old1, block)
    elif old2 in txt:
        txt = txt.replace(old2, block)
    else:
        print("⚠️ Je n'ai pas trouvé la ligne de génération de réponse. main.py devra être vérifié.")
else:
    print("main.py contient déjà la détection pub.")

p.write_text(txt, encoding="utf-8")
print("✅ main.py vérifié / patché.")
