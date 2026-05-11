import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

import pyperclip
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from chrome_control import attach_driver, ensure_whatsapp_tab, wait_for_whatsapp_ready
from bot_core import get_state, set_state

try:
    from campaign_context import detect_campaign_from_chat
except Exception:
    detect_campaign_from_chat = None

try:
    from runtime_message_reader import get_actionable_incoming_messages
except Exception:
    get_actionable_incoming_messages = None

try:
    from autonomous_sales_engine import decide_reply
except Exception:
    decide_reply = None

try:
    from conversation_brain import generate_human_sales_reply
except Exception:
    generate_human_sales_reply = None

try:
    from message_audit import audit_chat_messages, print_audit_rows
except Exception:
    audit_chat_messages = None
    print_audit_rows = None

from autonomous_patrol import patrol_next_chat
from human_pause import should_pause_for_human

try:
    from lead_memory import remember_incoming, remember_outgoing, get_due_followup
except Exception:
    remember_incoming = None
    remember_outgoing = None
    get_due_followup = None

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
LOG_PATH = BASE_DIR / "conversations_log.jsonl"
DECISIONS_PATH = BASE_DIR / "bot_decisions.jsonl"
HANDLED_PATH = BASE_DIR / "handled_incoming.json"

LAST_CHAT = None

def load_settings():
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig")) if SETTINGS_PATH.exists() else {}
    except Exception:
        data = {}

    defaults = {
        "send_automatically": True,
        "autonomous_mode_enabled": True,
        "auto_scan_unread_chats": True,
        "patrol_use_unread_filter": True,
        "patrol_coordinate_fallback": True,
        "patrol_changed_chats": True,
        "patrol_new_rows": True,
        "patrol_recent_limit": 8,
        "patrol_min_seconds_between_same_chat": 8,
        "patrol_coordinate_cycle_seconds": 3,
        "patrol_after_click_wait_seconds": 1.0,
        "audit_all_visible_messages": True,
        "confidence_required": 0.88,
        "auto_send_only_safe": True,
        "auto_send_delay_seconds": 0.8,
        "skip_if_message_box_not_empty": False,
        "poll_seconds": 1.3,
        "auto_followup_enabled": False
    }

    for k, v in defaults.items():
        data.setdefault(k, v)

    return data

def log_jsonl(path, row):
    try:
        row["time"] = datetime.now().isoformat(timespec="seconds")
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass

def load_handled():
    try:
        if HANDLED_PATH.exists():
            return json.loads(HANDLED_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {}

def save_handled(data):
    try:
        HANDLED_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def fp(chat, msg):
    return hashlib.sha1(f"{chat}::{msg}".encode("utf-8", errors="ignore")).hexdigest()[:24]

def already_handled(chat, msg):
    return fp(chat, msg) in load_handled()

def mark_handled(chat, msg, intent):
    data = load_handled()
    data[fp(chat, msg)] = {
        "chat": chat,
        "message": msg,
        "intent": intent,
        "time": datetime.now().isoformat(timespec="seconds")
    }

    if len(data) > 1500:
        keys = list(data.keys())[-1500:]
        data = {k: data[k] for k in keys}

    save_handled(data)

def get_chat_title(driver):
    try:
        headers = driver.find_elements(By.CSS_SELECTOR, "header span[dir='auto']")
        for h in headers:
            txt = h.text.strip()
            if txt and len(txt) < 90:
                return txt
    except Exception:
        pass
    return "conversation_ouverte"

def find_message_box(driver):
    selectors = [
        "footer div[contenteditable='true'][role='textbox']",
        "footer div[contenteditable='true']",
        "div[contenteditable='true'][role='textbox']"
    ]

    for css in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, css)
            for el in els:
                if el.is_displayed():
                    return el
        except Exception:
            continue

    try:
        return driver.find_element(By.XPATH, "//footer//div[@contenteditable='true']")
    except NoSuchElementException:
        return None

def box_text(box):
    try:
        return (box.text or "").strip()
    except Exception:
        return ""

def paste_reply(driver, text, send=False):
    settings = load_settings()
    box = find_message_box(driver)

    if not box:
        return False, "zone_message_introuvable"

    current = box_text(box)
    if settings.get("skip_if_message_box_not_empty", False) and current:
        return False, "brouillon_deja_present_non_ecrase"

    try:
        box.click()
        time.sleep(0.15)

        for _ in range(3):
            box.send_keys(Keys.CONTROL, "a")
            time.sleep(0.05)
            box.send_keys(Keys.BACKSPACE)
            time.sleep(0.05)

        pyperclip.copy(text)
        box.send_keys(Keys.CONTROL, "v")
        time.sleep(float(settings.get("auto_send_delay_seconds", 0.8)))

        if send:
            box.send_keys(Keys.ENTER)

        return True, "envoye" if send else "colle"

    except Exception as e:
        return False, "erreur_paste:" + repr(e)

def fallback_reply(message, chat):
    if decide_reply:
        return decide_reply(message, message.split("\n")[-1], chat)

    if generate_human_sales_reply:
        return generate_human_sales_reply(message, chat)

    return {
        "reply": "Bonjour 👋 Dites-moi ce que vous voulez commander ou envoyez votre demande.",
        "confidence": 0.75,
        "intent": "basic_fallback",
        "safe_to_auto_send": False,
        "_no_media": True
    }

def do_precheck(driver, chat):
    if not detect_campaign_from_chat:
        return "precheck_unavailable"

    try:
        camp = detect_campaign_from_chat(driver, chat)
        if not camp:
            return "no_campaign"

        if camp.get("state_patch"):
            patch = camp.get("state_patch", {})
            patch["needs_campaign_label"] = False
            set_state(chat, patch)
            return "campaign_detected"

        if camp.get("unknown"):
            set_state(chat, {
                "needs_campaign_label": False,
                "unknown_campaign_hash": camp.get("hash", "")
            })
            return "unknown_campaign_not_blocked"

    except Exception as e:
        return "precheck_error:" + repr(e)

    return "precheck_done"

def read_messages(driver, chat):
    if not get_actionable_incoming_messages:
        return []

    try:
        return get_actionable_incoming_messages(driver, chat, limit=55)
    except TypeError:
        return get_actionable_incoming_messages(driver, chat)
    except Exception:
        return []

def main():
    global LAST_CHAT

    s = load_settings()

    print("=" * 94)
    print("FASTBOT V11 HARD AUTONOMY")
    print("=" * 94)
    print("Mode autonome :", s.get("autonomous_mode_enabled"))
    print("Coord fallback :", s.get("patrol_coordinate_fallback"))
    print("Envoi auto     :", s.get("send_automatically"))
    print("Admin          : admin_control_gui.bat")
    print("Calibration    : calibrate_ui.bat")
    print("=" * 94)

    driver = attach_driver()
    ensure_whatsapp_tab(driver)
    wait_for_whatsapp_ready(driver)

    while True:
        try:
            s = load_settings()

            # Si tu bouges la souris ou tapes au clavier, le bot te laisse la main.
            if should_pause_for_human(s):
                time.sleep(float(s.get("human_pause_poll_seconds", 0.5)))
                continue

            chat = get_chat_title(driver)

            if chat != LAST_CHAT:
                print("")
                print("➡️ Conversation active :", chat)
                LAST_CHAT = chat

            if s.get("audit_all_visible_messages", True) and audit_chat_messages:
                rows = audit_chat_messages(driver, chat)
                if print_audit_rows:
                    print_audit_rows(rows)

            precheck = do_precheck(driver, chat)

            messages = read_messages(driver, chat)

            if not messages:
                if get_due_followup:
                    follow = get_due_followup(chat, s)
                    if follow and follow.get("reply"):
                        conf = float(follow.get("confidence", 0))
                        safe = bool(follow.get("safe_to_auto_send", False))
                        should_send = bool(s.get("send_automatically")) and conf >= float(s.get("confidence_required", 0.88))
                        if s.get("auto_send_only_safe", True):
                            should_send = should_send and safe

                        ok, action = paste_reply(driver, follow["reply"], send=should_send)
                        print("RELANCE :", action, follow["reply"])
                        if remember_outgoing:
                            remember_outgoing(chat, follow["reply"], follow.get("intent", "auto_followup"), should_send and ok)

                patrol_next_chat(driver, s)
                time.sleep(float(s.get("poll_seconds", 1.3)))
                continue

            combined = "\n".join(messages).strip()

            if already_handled(chat, combined):
                patrol_next_chat(driver, s)
                time.sleep(float(s.get("poll_seconds", 1.3)))
                continue

            if remember_incoming:
                remember_incoming(chat, messages)

            result = fallback_reply(combined, chat)

            try:
                patch = result.get("_state_patch") or {}
                if patch:
                    set_state(chat, patch)
            except Exception:
                pass

            reply = (result.get("reply") or "").strip()
            intent = result.get("intent", "")
            conf = float(result.get("confidence", 0))
            safe = bool(result.get("safe_to_auto_send", False))

            should_send = bool(s.get("send_automatically", True)) and conf >= float(s.get("confidence_required", 0.88))
            if bool(s.get("auto_send_only_safe", True)):
                should_send = should_send and safe

            print("-" * 94)
            print("Conversation :", chat)
            print("Precheck     :", precheck)
            print("Messages     :")
            for i, m in enumerate(messages, 1):
                print(f"{i}. {m}")
            print("Intent       :", intent)
            print("Confiance    :", conf)
            print("Safe         :", safe)
            print("Auto-send    :", should_send)

            action = "no_reply"
            ok = False

            if reply and conf >= 0.35:
                ok, action = paste_reply(driver, reply, send=should_send)
                print("Action       :", action)
                print("Réponse      :")
                print(reply)
            else:
                print("Silence / aucune réponse.")

            row = {
                "chat": chat,
                "precheck": precheck,
                "messages": messages,
                "reply": reply,
                "intent": intent,
                "confidence": conf,
                "safe": safe,
                "auto_sent": should_send and ok,
                "action": action,
                "debug": result.get("debug", {})
            }

            log_jsonl(LOG_PATH, row)
            log_jsonl(DECISIONS_PATH, row)

            if remember_outgoing:
                remember_outgoing(chat, reply, intent, should_send and ok)

            mark_handled(chat, combined, intent)

            patrol_next_chat(driver, s)

            time.sleep(float(s.get("poll_seconds", 1.3)))

        except KeyboardInterrupt:
            print("\nArrêt demandé.")
            break
        except Exception as e:
            print("Erreur boucle principale :", repr(e))
            log_jsonl(LOG_PATH, {"error": repr(e), "where": "main_v11"})
            time.sleep(2)

if __name__ == "__main__":
    main()
