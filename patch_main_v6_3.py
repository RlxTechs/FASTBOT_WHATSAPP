from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from auto_inbox import open_next_unread_chat" not in txt:
    txt = txt.replace(
        "from campaign_context import detect_campaign_from_chat",
        "from campaign_context import detect_campaign_from_chat\nfrom auto_inbox import open_next_unread_chat"
    )

# Après recent_messages = ..., si aucun message et auto_scan actif, ouvrir conversation non lue.
old = '''if recent_messages:
                combined_msg = "\\n".join(recent_messages)'''

new = '''if not recent_messages and bool(s.get("auto_scan_unread_chats", False)):
                try:
                    opened = open_next_unread_chat(driver)
                    if opened:
                        time.sleep(float(s.get("auto_scan_when_idle_seconds", 4)))
                        continue
                except Exception as auto_err:
                    print("Auto-inbox erreur :", repr(auto_err))

            if recent_messages:
                combined_msg = "\\n".join(recent_messages)'''

if old in txt and "open_next_unread_chat(driver)" not in txt:
    txt = txt.replace(old, new)

# Ne pas prechecker en boucle quand WhatsApp n’a pas de conversation active.
old2 = '''chat_title = get_chat_title(driver)
            chat_changed = chat_title != LAST_CHAT_TITLE'''

new2 = '''chat_title = get_chat_title(driver)

            if bool(s.get("skip_conversation_ouverte", True)) and chat_title == "conversation_ouverte":
                if bool(s.get("auto_scan_unread_chats", False)):
                    try:
                        open_next_unread_chat(driver)
                    except Exception:
                        pass
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            chat_changed = chat_title != LAST_CHAT_TITLE'''

if old2 in txt and 'chat_title == "conversation_ouverte"' not in txt:
    txt = txt.replace(old2, new2)

# Remplacer le handler d’erreur pour InvalidSessionId.
old3 = '''except Exception as e:
            print("Erreur capturée, le bot continue :", repr(e))
            log_event({"error": repr(e), "where": "main_loop"})
            time.sleep(3)'''

new3 = '''except Exception as e:
            if e.__class__.__name__ == "InvalidSessionIdException":
                print("Session Chrome perdue. Ferme Chrome contrôlé puis relance .\\\\start_bot.bat")
                log_event({"error": repr(e), "where": "main_loop", "fatal": True})
                break

            print("Erreur capturée, le bot continue :", repr(e))
            log_event({"error": repr(e), "where": "main_loop"})
            time.sleep(3)'''

if old3 in txt:
    txt = txt.replace(old3, new3)

p.write_text(txt, encoding="utf-8")
print("✅ main.py patché : auto-inbox optionnel + InvalidSession propre.")
