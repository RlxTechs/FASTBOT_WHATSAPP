from pathlib import Path
import re

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

new_func = r'''
def paste_reply(driver, reply_text, send=False):
    settings = load_settings()
    box = find_message_box(driver)
    if not box:
        return False, "zone_message_introuvable"

    current_draft = get_box_text(box)
    if settings.get("skip_if_message_box_not_empty", True) and current_draft:
        return False, "brouillon_deja_present_non_ecrase"

    try:
        box.click()
        time.sleep(0.15)

        # Nettoyage robuste du champ message
        for _ in range(3):
            box.send_keys(Keys.CONTROL, "a")
            time.sleep(0.05)
            box.send_keys(Keys.BACKSPACE)
            time.sleep(0.05)

        # Vérification après nettoyage
        current_after_clear = get_box_text(box)
        if current_after_clear.strip():
            return False, "champ_non_vide_apres_nettoyage"

        pyperclip.copy(reply_text)
        box.send_keys(Keys.CONTROL, "v")
        time.sleep(float(settings.get("auto_send_delay_seconds", 0.8)))

        if send:
            box.send_keys(Keys.ENTER)

        return True, "envoye" if send else "colle"

    except Exception as e:
        return False, "erreur_paste:" + repr(e)
'''

pattern = r"def paste_reply\(driver, reply_text, send=False\):.*?\n(?=def consume_force_rescan_flag)"
if re.search(pattern, txt, flags=re.S):
    txt = re.sub(pattern, new_func + "\n\n", txt, flags=re.S)
else:
    print("⚠️ Fonction paste_reply non trouvée automatiquement.")

p.write_text(txt, encoding="utf-8")
print("✅ main.py : paste_reply rendu plus robuste.")
