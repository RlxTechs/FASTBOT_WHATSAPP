from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from media_engine import select_media_for_reply, send_media_files" not in txt:
    txt = txt.replace(
        "from campaign_context import detect_campaign_from_chat",
        "from campaign_context import detect_campaign_from_chat\nfrom media_engine import select_media_for_reply, send_media_files"
    )

old = '''ok, action = paste_reply(driver, reply, send=should_send)
                        print("Action :", action)
                        print("Réponse :")
                        print(reply)'''

new = '''ok, action = paste_reply(driver, reply, send=should_send)
                        print("Action :", action)
                        print("Réponse :")
                        print(reply)

                        # V5.9 : envoyer les images liées au produit / plat / réponse
                        try:
                            media_files = select_media_for_reply(combined_msg, chat_title, result)
                            if media_files:
                                print("Médias détectés :", media_files)
                                if should_send:
                                    media_result = send_media_files(driver, media_files)
                                    print("Médias envoyés :", media_result)
                                else:
                                    print("Mode non-auto : médias non envoyés automatiquement.")
                        except Exception as media_err:
                            print("Erreur envoi médias :", repr(media_err))'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc paste_reply exact non trouvé. On va chercher une variante.")
    old2 = "ok, action = paste_reply(driver, reply, send=should_send)"
    if old2 in txt and "select_media_for_reply(combined_msg" not in txt:
        txt = txt.replace(old2, new.split("\n")[0] + "\n" + "\n".join(new.split("\n")[1:]))
    else:
        print("⚠️ Patch média non appliqué automatiquement. main.py doit être vérifié.")

p.write_text(txt, encoding="utf-8")
print("✅ main.py patché avec envoi médias.")
