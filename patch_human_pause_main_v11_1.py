from pathlib import Path

p = Path("main_v11.py")
txt = p.read_text(encoding="utf-8-sig")

if "from human_pause import should_pause_for_human" not in txt:
    txt = txt.replace(
        "from autonomous_patrol import patrol_next_chat",
        "from autonomous_patrol import patrol_next_chat\nfrom human_pause import should_pause_for_human"
    )

old = '''while True:
        try:
            s = load_settings()

            chat = get_chat_title(driver)'''

new = '''while True:
        try:
            s = load_settings()

            # Si tu bouges la souris ou tapes au clavier, le bot te laisse la main.
            if should_pause_for_human(s):
                time.sleep(float(s.get("human_pause_poll_seconds", 0.5)))
                continue

            chat = get_chat_title(driver)'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Bloc principal non trouvé exactement. Vérifie main_v11.py")

p.write_text(txt, encoding="utf-8")
print("✅ main_v11.py : pause humaine branchée.")
