import json
import time
from pathlib import Path

import pyautogui

BASE_DIR = Path(__file__).resolve().parent
CFG = BASE_DIR / "ui_coordinates.json"

def countdown(label, seconds=5):
    print("\n" + "=" * 80)
    print(label)
    print("Place ta souris au bon endroit. Capture dans", seconds, "secondes...")
    for i in range(seconds, 0, -1):
        print(i, end=" ", flush=True)
        time.sleep(1)
    print()
    return pyautogui.position()

def main():
    print("=" * 80)
    print("CALIBRAGE FASTBOT V11")
    print("=" * 80)
    print("Laisse WhatsApp Web visible comme dans ta vidéo.")
    print("On va enregistrer les coordonnées des boutons et lignes.")
    print("Ne clique pas, place juste la souris au bon endroit pendant le compte à rebours.")

    all_pos = countdown("1) Place la souris sur le bouton/onglet : Toutes")
    unread_pos = countdown("2) Place la souris sur le bouton/onglet : Non lues")
    first_row = countdown("3) Place la souris au centre de la 1ère conversation dans la liste")
    second_row = countdown("4) Place la souris au centre de la 2ème conversation dans la liste")

    row_gap = second_row.y - first_row.y
    if row_gap <= 20 or row_gap > 120:
        row_gap = 72

    data = {
        "enabled": True,
        "filter_all": [all_pos.x, all_pos.y],
        "filter_unread": [unread_pos.x, unread_pos.y],
        "first_chat": [first_row.x, first_row.y],
        "row_gap": row_gap,
        "max_rows": 8,
        "screen_size": list(pyautogui.size())
    }

    CFG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n✅ Coordonnées sauvegardées dans ui_coordinates.json")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    input("\nAppuie sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
