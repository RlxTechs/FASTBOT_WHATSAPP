from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from smart_reply import generate_smart_reply" not in txt:
    txt = txt.replace(
        "from bot_core import generate_reply",
        "from smart_reply import generate_smart_reply\nfrom bot_core import get_state, set_state\nfrom campaign_context import detect_campaign_from_chat"
    )

if "from campaign_context import detect_campaign_from_chat" not in txt:
    txt = txt.replace(
        "from smart_reply import generate_smart_reply",
        "from smart_reply import generate_smart_reply\nfrom bot_core import get_state, set_state\nfrom campaign_context import detect_campaign_from_chat"
    )

if "detect_campaign_from_chat(driver, chat_title)" not in txt:
    old = "result = generate_smart_reply(last_msg, chat_id=chat_title)"
    block = """try:
                        state = get_state(chat_title)
                        if not state.get("campaign_id"):
                            camp = detect_campaign_from_chat(driver, chat_title)
                            if camp:
                                if camp.get("unknown"):
                                    unknown_hash = camp.get("hash", "")
                                    print("")
                                    print("⚠️ PUB FACEBOOK INCONNUE DÉTECTÉE")
                                    print("Hash :", unknown_hash)
                                    print("Va dans campaign_captures puis lance campaign_admin.bat pour l'étiqueter.")
                                    print("Si c'est le menu nourriture, tu peux lancer label_last_unknown_as_menu.bat")
                                    print("Le bot ne répondra pas au hasard.")
                                    print("")
                                    set_state(chat_title, {
                                        "needs_campaign_label": True,
                                        "unknown_campaign_hash": unknown_hash,
                                        "unknown_campaign_source": camp.get("source", "facebook_ad_card_unknown"),
                                        "unknown_campaign_image": "campaign_captures/unknown_" + str(unknown_hash) + ".png"
                                    })
                                else:
                                    patch = camp.get("state_patch", {})
                                    patch["needs_campaign_label"] = False
                                    set_state(chat_title, patch)
                                    print("Contexte pub détecté :", camp.get("label"), "| source :", camp.get("source"))
                    except Exception as ctx_err:
                        print("Contexte pub non détecté :", repr(ctx_err))

                    result = generate_smart_reply(last_msg, chat_id=chat_title)"""
    if old in txt:
        txt = txt.replace(old, block)
    else:
        print("⚠️ Ligne generate_smart_reply non trouvée. main.py contient peut-être déjà un patch.")

p.write_text(txt, encoding="utf-8")
print("main.py vérifié.")
