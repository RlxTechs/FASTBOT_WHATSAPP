import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

STATE_PATH = BASE_DIR / "patrol_state.json"
DEBUG_PATH = BASE_DIR / "patrol_debug.jsonl"
COORD_PATH = BASE_DIR / "ui_coordinates.json"

def now():
    return time.time()

def ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def sha(text):
    return hashlib.sha1(str(text or "").encode("utf-8", errors="ignore")).hexdigest()[:20]

def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def log_debug(row):
    try:
        row["time"] = ts()
        with DEBUG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass

def state():
    return load_json(STATE_PATH, {"rows": {}, "coord_cursor": 0, "last_click_at": 0})

def save_state(data):
    save_json(STATE_PATH, data)

def coords():
    return load_json(COORD_PATH, {})

def text_of(el):
    try:
        return (el.text or "").strip()
    except Exception:
        return ""

def html_of(el):
    try:
        return (el.get_attribute("innerHTML") or "").lower()
    except Exception:
        return ""

def aria_of(el):
    try:
        return (el.get_attribute("aria-label") or "").lower()
    except Exception:
        return ""

def safe_click(driver, el):
    try:
        el.location_once_scrolled_into_view
        time.sleep(0.1)
        el.click()
        return True
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        pass

    try:
        ActionChains(driver).move_to_element(el).pause(0.1).click().perform()
        return True
    except Exception:
        return False

def click_text_filter(driver, label):
    xpaths = [
        f"//*[normalize-space()='{label}']",
        f"//*[contains(normalize-space(), '{label}')]"
    ]

    for xp in xpaths:
        try:
            els = driver.find_elements(By.XPATH, xp)
            for el in els:
                if el.is_displayed():
                    if safe_click(driver, el):
                        time.sleep(0.6)
                        log_debug({"event": "filter_clicked_html", "filter": label})
                        return True
        except Exception:
            continue

    log_debug({"event": "filter_click_html_failed", "filter": label})
    return False

def coord_click(x, y, label=""):
    if not pyautogui:
        log_debug({"event": "coord_click_failed", "reason": "pyautogui_missing", "label": label})
        return False

    try:
        pyautogui.click(int(x), int(y))
        time.sleep(0.7)
        log_debug({"event": "coord_click", "label": label, "x": int(x), "y": int(y)})
        return True
    except Exception as e:
        log_debug({"event": "coord_click_failed", "label": label, "error": repr(e)})
        return False

def click_filter(driver, label, settings):
    # 1) HTML
    if click_text_filter(driver, label):
        return True

    # 2) Coordonnées
    c = coords()
    if not c.get("enabled"):
        return False

    if label.lower().startswith("non"):
        pos = c.get("filter_unread")
    else:
        pos = c.get("filter_all")

    if not pos:
        return False

    return coord_click(pos[0], pos[1], "filter_" + label)

def is_left_chat_row(row):
    try:
        r = row.rect
        x = float(r.get("x", 9999))
        w = float(r.get("width", 0))
        h = float(r.get("height", 0))

        if x > 550:
            return False
        if h < 40:
            return False
        if w < 180 or w > 760:
            return False

        return True
    except Exception:
        return True

def looks_like_chat_row(row):
    txt = text_of(row)
    if not txt:
        return False

    low = txt.lower()

    banned = [
        "communautés", "communautes", "chaînes", "chaines",
        "statut", "nouvelle discussion", "archivées", "archivees",
        "paramètres", "parametres", "rechercher", "menu"
    ]

    if any(b in low for b in banned):
        return False

    return is_left_chat_row(row)

def get_chat_rows(driver):
    selectors = [
        "div[role='listitem']",
        "div[role='row']",
        "div[aria-label*='Discussion'] div[role='listitem']",
        "div[aria-label*='Chat'] div[role='listitem']"
    ]

    best = []

    for css in selectors:
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, css)
            rows = [r for r in rows if looks_like_chat_row(r)]
            if len(rows) > len(best):
                best = rows
        except Exception:
            continue

    return best

def row_title(txt):
    lines = [x.strip() for x in str(txt or "").splitlines() if x.strip()]
    return lines[0][:80] if lines else "unknown"

def row_has_unread(row):
    txt = text_of(row).lower()
    html = html_of(row)
    aria = aria_of(row)

    signals = [
        "non lu", "non lus", "unread", "unread-count",
        "data-icon=\"unread-count\"",
        "aria-label=\"1\"", "aria-label=\"2\"", "aria-label=\"3\""
    ]

    if any(s in txt for s in ["non lu", "non lus", "unread"]):
        return True

    if any(s in html for s in signals):
        return True

    if any(s in aria for s in ["non lu", "non lus", "unread"]):
        return True

    return False

def snapshot_rows(driver, assume_unread=False):
    rows = get_chat_rows(driver)
    out = []

    for i, row in enumerate(rows):
        txt = text_of(row)
        if not txt:
            continue

        title = row_title(txt)

        out.append({
            "index": i,
            "title": title,
            "signature": sha(title),
            "preview_hash": sha(txt),
            "text": txt,
            "unread": True if assume_unread else row_has_unread(row),
            "row": row
        })

    return out

def choose_html_candidate(driver, settings):
    cooldown = float(settings.get("patrol_min_seconds_between_same_chat", 8))
    st = state()
    known = st.setdefault("rows", {})

    # Étape 1 : onglet Non lues.
    if bool(settings.get("patrol_use_unread_filter", True)):
        click_filter(driver, "Non lues", settings)
        rows = snapshot_rows(driver, assume_unread=True)

        if rows:
            for item in rows:
                sig = item["signature"]
                last_click = float(known.get(sig, {}).get("last_clicked_at", 0))
                if now() - last_click >= cooldown:
                    item["reason"] = "unread_filter_row_html"
                    return item

    # Étape 2 : toutes + changements d’aperçu.
    click_filter(driver, "Toutes", settings)
    rows = snapshot_rows(driver, assume_unread=False)

    candidates = []

    for item in rows:
        sig = item["signature"]
        prev = known.get(sig, {})
        old_hash = prev.get("preview_hash")
        last_click = float(prev.get("last_clicked_at", 0))
        too_recent = now() - last_click < cooldown
        reason = ""

        if item["unread"] and not too_recent:
            reason = "unread_badge_html"
        elif bool(settings.get("patrol_changed_chats", True)) and old_hash and old_hash != item["preview_hash"] and not too_recent:
            reason = "preview_changed_html"
        elif bool(settings.get("patrol_new_rows", True)) and not old_hash and item["index"] < int(settings.get("patrol_recent_limit", 8)) and not too_recent:
            reason = "new_recent_row_html"

        known[sig] = {
            "title": item["title"],
            "preview_hash": item["preview_hash"],
            "last_seen_at": now(),
            "last_clicked_at": last_click
        }

        if reason:
            item["reason"] = reason
            candidates.append(item)

    save_state(st)

    if not candidates:
        log_debug({
            "event": "no_html_candidate",
            "rows_found": len(rows),
            "top": [{"i": x["index"], "title": x["title"], "unread": x["unread"], "text": x["text"][:120]} for x in rows[:8]]
        })
        return None

    order = {"unread_badge_html": 1, "preview_changed_html": 2, "new_recent_row_html": 3}
    candidates.sort(key=lambda x: (order.get(x["reason"], 99), x["index"]))
    return candidates[0]

def click_html_candidate(driver, item):
    ok = safe_click(driver, item["row"])
    if not ok:
        return False

    st = state()
    sig = item["signature"]
    st.setdefault("rows", {}).setdefault(sig, {})
    st["rows"][sig]["title"] = item["title"]
    st["rows"][sig]["preview_hash"] = item["preview_hash"]
    st["rows"][sig]["last_clicked_at"] = now()
    st["rows"][sig]["last_seen_at"] = now()
    save_state(st)

    log_debug({"event": "clicked_html", "title": item["title"], "reason": item["reason"]})
    return True

def patrol_by_coordinates(driver, settings):
    c = coords()
    if not c.get("enabled"):
        log_debug({"event": "coord_mode_disabled_or_not_calibrated"})
        return False

    cooldown = float(settings.get("patrol_coordinate_cycle_seconds", 3))
    st = state()
    last = float(st.get("last_coord_click_at", 0))

    if now() - last < cooldown:
        return False

    unread = c.get("filter_unread")
    first = c.get("first_chat")

    if not unread or not first:
        log_debug({"event": "coord_missing_points"})
        return False

    coord_click(unread[0], unread[1], "coord_filter_non_lues")

    cursor = int(st.get("coord_cursor", 0))
    max_rows = int(c.get("max_rows", 8))
    gap = int(c.get("row_gap", 72))

    x = int(first[0])
    y = int(first[1]) + (cursor * gap)

    ok = coord_click(x, y, "coord_chat_row_" + str(cursor + 1))

    st["coord_cursor"] = (cursor + 1) % max_rows
    st["last_coord_click_at"] = now()
    save_state(st)

    if ok:
        print("")
        print("🤖 PATROUILLE COORDONNÉES — clic conversation")
        print("   Ligne :", cursor + 1)
        print("   x/y   :", x, y)
        log_debug({"event": "clicked_coordinates", "row": cursor + 1, "x": x, "y": y})
        return True

    return False

def patrol_next_chat(driver, settings):
    if not bool(settings.get("autonomous_mode_enabled", False)):
        return False

    try:
        driver.maximize_window()
    except Exception:
        pass

    # Méthode 1 : HTML/Selenium.
    candidate = choose_html_candidate(driver, settings)
    if candidate:
        print("")
        print("🤖 PATROUILLE HTML — ouverture conversation")
        print("   Contact :", candidate.get("title"))
        print("   Raison  :", candidate.get("reason"))

        if click_html_candidate(driver, candidate):
            time.sleep(float(settings.get("patrol_after_click_wait_seconds", 1.0)))
            return True

    # Méthode 2 : coordonnées écran, forcée.
    if bool(settings.get("patrol_coordinate_fallback", True)):
        ok = patrol_by_coordinates(driver, settings)
        if ok:
            time.sleep(float(settings.get("patrol_after_click_wait_seconds", 1.0)))
            return True

    return False
