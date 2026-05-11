import json
import hashlib
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

TIMELINE_PATH = BASE_DIR / "full_timeline.jsonl"
RUNTIME_PATH = BASE_DIR / "bot_runtime_log.jsonl"
SEEN_PATH = BASE_DIR / "seen_timeline_hashes.json"

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_seen():
    try:
        if SEEN_PATH.exists():
            return json.loads(SEEN_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {}

def save_seen(data):
    try:
        if len(data) > 3000:
            keys = list(data.keys())[-3000:]
            data = {k: data[k] for k in keys}
        SEEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def fp(*parts):
    raw = "::".join(str(x) for x in parts).encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:24]

def append_jsonl(path, row):
    row.setdefault("time", now())
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def log_event(event_type, chat="", data=None):
    append_jsonl(RUNTIME_PATH, {
        "event_type": event_type,
        "chat": chat,
        "data": data or {}
    })

def classify_text(text):
    low = (text or "").lower()
    if "vous avez supprimé ce message" in low or "vous avez supprime ce message" in low:
        return "deleted_message_marker"
    if "appel vocal manqué" in low or "appel vidéo manqué" in low or "appel video manque" in low:
        return "missed_call_marker"
    return "message"

def capture_visible_timeline(driver, chat_title, limit=40):
    """
    Capture ce qui est visible dans la conversation :
    - messages clients
    - messages envoyés par toi / bot
    - messages supprimés
    - appels manqués
    """
    seen = load_seen()
    added = 0

    try:
        bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
        tail = bubbles[-limit:] if bubbles else []

        for idx, b in enumerate(tail):
            try:
                cls = b.get_attribute("class") or ""
                direction = "incoming" if "message-in" in cls else "outgoing" if "message-out" in cls else "unknown"

                text = (b.text or "").strip()
                if not text:
                    continue

                kind = classify_text(text)
                h = fp(chat_title, direction, kind, text)

                if h in seen:
                    continue

                row = {
                    "hash": h,
                    "chat": chat_title,
                    "direction": direction,
                    "kind": kind,
                    "text": text
                }

                append_jsonl(TIMELINE_PATH, row)
                seen[h] = {"time": now(), "chat": chat_title, "kind": kind}
                added += 1
            except Exception as e:
                log_event("timeline_bubble_error", chat_title, {"error": repr(e)})

    except Exception as e:
        log_event("timeline_capture_error", chat_title, {"error": repr(e)})

    if added:
        save_seen(seen)

    return added
