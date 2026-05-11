import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from selenium.webdriver.common.by import By

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

AUDIT_LOG = BASE_DIR / "audit_messages.jsonl"
AUDIT_SEEN = BASE_DIR / "audit_seen.json"

def load_seen():
    try:
        if AUDIT_SEEN.exists():
            return json.loads(AUDIT_SEEN.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {}

def save_seen(data):
    try:
        AUDIT_SEEN.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def fp(chat: str, direction: str, text: str) -> str:
    raw = f"{chat}::{direction}::{text.strip()}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:24]

def append_jsonl(path: Path, row: Dict[str, Any]):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def classify_text(text: str) -> Dict[str, Any]:
    low = (text or "").lower()
    return {
        "deleted_marker": "vous avez supprimé ce message" in low or "vous avez supprime ce message" in low,
        "missed_call": "appel vocal manqué" in low or "appel vocal manque" in low,
        "system_hint": "rappelez des personnes" in low or "messages et appels" in low,
        "empty": not bool((text or "").strip())
    }

def extract_text_from_bubble(bubble) -> str:
    parts = []
    try:
        spans = bubble.find_elements(By.CSS_SELECTOR, "span.selectable-text.copyable-text")
        for s in spans:
            tx = (s.text or "").strip()
            if tx:
                parts.append(tx)
    except Exception:
        pass

    if parts:
        return "\n".join(parts).strip()

    try:
        return (bubble.text or "").strip()
    except Exception:
        return ""

def audit_chat_messages(driver, chat_title: str, limit: int = 45) -> List[Dict[str, Any]]:
    seen = load_seen()
    new_rows = []

    try:
        bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    except Exception:
        return []

    for bubble in bubbles[-limit:]:
        try:
            cls = bubble.get_attribute("class") or ""
            direction = "outgoing" if "message-out" in cls else "incoming"
            text = extract_text_from_bubble(bubble)
            flags = classify_text(text)

            if flags["empty"]:
                continue

            key = fp(chat_title, direction, text)
            if key in seen:
                continue

            row = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "chat": chat_title,
                "direction": direction,
                "text": text,
                "flags": flags,
                "source": "whatsapp_visible_bubble"
            }

            append_jsonl(AUDIT_LOG, row)
            seen[key] = row["time"]
            new_rows.append(row)

        except Exception:
            continue

    if len(seen) > 3000:
        keys = list(seen.keys())[-3000:]
        seen = {k: seen[k] for k in keys}

    save_seen(seen)
    return new_rows

def print_audit_rows(rows):
    if not rows:
        return

    print("")
    print("🧾 AUDIT — nouveaux messages visibles dans WhatsApp")
    print("-" * 94)

    for row in rows:
        direction = row.get("direction")
        text = row.get("text", "").strip()
        flags = row.get("flags", {})

        if flags.get("deleted_marker"):
            label = "🗑️ SUPPRIMÉ"
        elif direction == "outgoing":
            label = "📤 MOI/BOT"
        else:
            label = "📥 CLIENT"

        print(f"{label} | {row.get('chat')} | {row.get('time')}")
        print(text)
        print("-" * 94)
