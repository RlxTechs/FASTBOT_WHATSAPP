import time
from selenium.webdriver.common.by import By

def row_text(row) -> str:
    try:
        return (row.text or "").strip()
    except Exception:
        return ""

def looks_like_chat_row(row) -> bool:
    txt = row_text(row)
    if not txt:
        return False

    low = txt.lower()
    bad = ["communautés", "chaines", "statut", "nouvelle discussion", "archivées", "paramètres"]
    if any(b in low for b in bad):
        return False

    return len(txt) > 2

def looks_unread(row) -> bool:
    txt = row_text(row).lower()
    if "non lu" in txt or "unread" in txt:
        return True

    try:
        html = (row.get_attribute("innerHTML") or "").lower()
        signals = [
            "unread",
            "non lu",
            "aria-label=\"1\"",
            "data-icon=\"unread-count\""
        ]
        return any(s in html for s in signals)
    except Exception:
        return False

def get_chat_rows(driver):
    selectors = [
        "div[role='listitem']",
        "div[aria-label*='Discussion'] div[role='listitem']",
        "div[aria-label*='Chat'] div[role='listitem']"
    ]

    for css in selectors:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, css)
            rows = [r for r in rows if looks_like_chat_row(r)]
            if rows:
                return rows
        except Exception:
            continue

    return []

def open_next_unread_chat(driver) -> bool:
    rows = get_chat_rows(driver)

    for row in rows:
        try:
            if row.is_displayed() and looks_unread(row):
                row.click()
                time.sleep(1.0)
                return True
        except Exception:
            continue

    return False

def open_recent_chat_candidate(driver, max_index: int = 8) -> bool:
    rows = get_chat_rows(driver)

    for row in rows[:max_index]:
        try:
            if row.is_displayed():
                row.click()
                time.sleep(0.8)
                return True
        except Exception:
            continue

    return False

def patrol_next_chat(driver, settings) -> bool:
    if not bool(settings.get("autonomous_mode_enabled", False)):
        return False

    if bool(settings.get("auto_scan_unread_chats", False)):
        if open_next_unread_chat(driver):
            return True

    if bool(settings.get("patrol_recent_chats", False)):
        return open_recent_chat_candidate(driver, int(settings.get("patrol_recent_limit", 8)))

    return False
