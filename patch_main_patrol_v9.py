from pathlib import Path

p = Path("main.py")
txt = p.read_text(encoding="utf-8-sig")

if "from autonomous_patrol import patrol_next_chat" not in txt:
    txt = txt.replace(
        "from chrome_control import attach_driver, ensure_whatsapp_tab, wait_for_whatsapp_ready",
        "from chrome_control import attach_driver, ensure_whatsapp_tab, wait_for_whatsapp_ready\nfrom autonomous_patrol import patrol_next_chat"
    )

# Remplacer les anciens appels si présents.
txt = txt.replace("open_next_unread_chat(driver)", "patrol_next_chat(driver, s)")
txt = txt.replace("open_next_unread_chat(driver, s)", "patrol_next_chat(driver, s)")

# Corriger cas où main utilise encore une condition trop limitée.
txt = txt.replace(
    'if bool(s.get("autonomous_mode_enabled", False)) and bool(s.get("auto_scan_unread_chats", False)):\n                    opened = patrol_next_chat(driver, s)',
    'if bool(s.get("autonomous_mode_enabled", False)):\n                    opened = patrol_next_chat(driver, s)'
)

p.write_text(txt, encoding="utf-8")
print("✅ main.py relié au patrouilleur V9.")
