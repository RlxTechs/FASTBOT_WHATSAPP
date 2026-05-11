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
from campaign_context import detect_campaign_from_chat
from runtime_message_reader import get_actionable_incoming_messages
from message_audit import audit_chat_messages, print_audit_rows
from autonomous_sales_engine import decide_reply
from lead_memory import remember_incoming, remember_outgoing, get_due_followup
from autonomous_patrol import patrol_next_chat

try:
    from media_engine import select_media_for_reply, send_media_files
except Exception:
    select_media_for_reply = None
    send_media_files = None

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
LOG_PATH = BASE_DIR / "conversations_log.jsonl"
BOT_DECISIONS = BASE_DIR / "bot_decisions.jsonl"
HANDLED_PATH = BASE_DIR / "handled_incoming.json"
FORCE_RESCAN_FLAG = BASE_DIR / "force_precheck.flag"

PRECHECK_CACHE = {}
LAST_CHAT_TITLE = None

def load_settings():
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig")) if SETTINGS_PATH.exists() else {}
    except Exception:
        data = {}

    defaults = {
        "send_automatically": True,
        "autonomous_mode_enabled": False,
        "auto_scan_unread_chats": False,
        "patrol_recent_chats": False,
        "patrol_recent_limit": 8,
        "auto_followup_enabled": False,
        "followup_after_minutes_1": 20,
        "followup_after_minutes_2": 60,
        "audit_all_visible_messages": True,
        "confidence_required": 0.88,
        "auto_send_only_safe": True,
        "auto_send_delay_seconds": 0.8,
        "skip_if_message_box_not_empty": True,
        "precheck_verbose": False,
        "block_on_unknown_campaign": False,
        "poll_seconds": 1.5,
        "auto_scan_when_idle_seconds": 4,
        "skip_conversation_ouverte": True,
        "precheck_rescan_known_after_seconds": 3600,
        "precheck_rescan_after_seconds": 300
    }

    for k, v in defaults.items():
        data.setdefault(k, v)

    return data

def append_jsonl(path, data):
    data["time"] = datetime.now().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def log_event(data):
    append_jsonl(LOG_PATH, data)

def log_decision(data):
    append_jsonl(BOT_DECISIONS, data)

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

def fingerprint(chat_title, combined_msg, context=""):
    raw = f"{chat_title}::{context}::{combined_msg.strip()}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:24]

def already_handled(chat_title, combined_msg, context=""):
    data = load_handled()
    return fingerprint(chat_title, combined_msg, context) in data

def mark_handled(chat_title, combined_msg, intent, action, context=""):
    data = load_handled()
    key = fingerprint(chat_title, combined_msg, context)

    data[key] = {
        "chat": chat_title,
        "message": combined_msg,
        "intent": intent,
        "action": action,
        "context": context,
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

def get_box_text(box):
    try:
        return (box.text or "").strip()
    except Exception:
        return ""

def paste_reply(driver, reply_text, send=False):
    settings = load_settings()
    box = find_message_box(driver)
    if not box:
        return False, "zone_message_introuvable"

    current = get_box_text(box)
    if settings.get("skip_if_message_box_not_empty", True) and current:
        return False, "brouillon_deja_present_non_ecrase"

    try:
        box.click()
        time.sleep(0.15)

        for _ in range(3):
            box.send_keys(Keys.CONTROL, "a")
            time.sleep(0.05)
            box.send_keys(Keys.BACKSPACE)
            time.sleep(0.05)

        if get_box_text(box).strip():
            return False, "champ_non_vide_apres_nettoyage"

        pyperclip.copy(reply_text)
        box.send_keys(Keys.CONTROL, "v")
        time.sleep(float(settings.get("auto_send_delay_seconds", 0.8)))

        if send:
            box.send_keys(Keys.ENTER)

        return True, "envoye" if send else "colle"

    except Exception as e:
        return False, "erreur_paste:" + repr(e)

def consume_force_rescan_flag():
    if FORCE_RESCAN_FLAG.exists():
        try:
            FORCE_RESCAN_FLAG.unlink()
        except Exception:
            pass
        return True
    return False

def should_precheck(chat_title, chat_changed):
    settings = load_settings()
    now_ts = time.time()
    state = get_state(chat_title)
    cache = PRECHECK_CACHE.get(chat_title, {})

    if consume_force_rescan_flag():
        return True, "manual_force_precheck"

    if chat_changed:
        return True, "chat_changed_force_scan"

    if state.get("campaign_id"):
        last_scan = float(cache.get("last_scan", 0))
        if now_ts - last_scan >= float(settings.get("precheck_rescan_known_after_seconds", 3600)):
            return True, "known_context_periodic_rescan"
        return False, "known_context_cached"

    last_scan = float(cache.get("last_scan", 0))
    if now_ts - last_scan >= float(settings.get("precheck_rescan_after_seconds", 300)):
        return True, "no_context_periodic_scan"

    return False, "precheck_cached"

def update_precheck_cache(chat_title, status, extra=None):
    data = {
        "last_scan": time.time(),
        "status": status
    }
    if extra:
        data.update(extra)
    PRECHECK_CACHE[chat_title] = data

def smart_campaign_precheck(driver, chat_title, chat_changed):
    settings = load_settings()
    do_scan, reason = should_precheck(chat_title, chat_changed)

    if not do_scan:
        return reason

    try:
        camp = detect_campaign_from_chat(driver, chat_title)
    except Exception as e:
        update_precheck_cache(chat_title, "precheck_error", {"error": repr(e)})
        if e.__class__.__name__ == "InvalidSessionIdException":
            raise
        return "precheck_error"

    if not camp:
        update_precheck_cache(chat_title, "no_campaign_card")
        return "no_campaign_card"

    if camp.get("unknown"):
        h = camp.get("hash", "")
        block_unknown = bool(settings.get("block_on_unknown_campaign", False))

        set_state(chat_title, {
            "needs_campaign_label": block_unknown,
            "unknown_campaign_hash": h,
            "unknown_campaign_source": camp.get("source", "facebook_ad_card_unknown"),
            "unknown_campaign_image": "campaign_captures/unknown_" + str(h) + ".png"
        })

        update_precheck_cache(chat_title, "unknown_campaign_logged", {"hash": h})

        if block_unknown:
            print("⚠️ Pub inconnue : conversation bloquée en attente admin. Hash :", h)
            return "unknown_campaign_blocked"

        print("⚠️ Pub inconnue mais conversation non bloquée. Hash :", h)
        return "unknown_campaign_continue"

    patch = camp.get("state_patch", {})
    patch["needs_campaign_label"] = False
    set_state(chat_title, patch)

    update_precheck_cache(chat_title, "campaign_detected", {
        "campaign_label": camp.get("label"),
        "source": camp.get("source")
    })

    if bool(settings.get("precheck_verbose", False)) or chat_changed:
        print("[PRECHECK] Contexte :", camp.get("label"), "| source :", camp.get("source"), "| raison :", reason)

    return "campaign_detected"

def maybe_send_media(driver, combined_msg, chat_title, result, should_send):
    if not select_media_for_reply or not send_media_files:
        return {"sent": 0, "error": "media_engine_unavailable"}

    try:
        media_files = select_media_for_reply(combined_msg, chat_title, result)
        if not media_files:
            return {"sent": 0, "error": ""}

        print("Médias détectés :", media_files)

        if should_send:
            media_result = send_media_files(driver, media_files)
            print("Médias envoyés :", media_result)
            return media_result

        return {"sent": 0, "error": "auto_send_disabled"}
    except Exception as e:
        print("Erreur médias :", repr(e))
        return {"sent": 0, "error": repr(e)}

def handle_followup(driver, chat_title, settings):
    follow = get_due_followup(chat_title, settings)
    if not follow:
        return False

    reply = follow.get("reply", "").strip()
    if not reply:
        return False

    conf = float(follow.get("confidence", 0))
    safe = bool(follow.get("safe_to_auto_send", False))

    should_send = bool(settings.get("send_automatically", False)) and conf >= float(settings.get("confidence_required", 0.88))
    if bool(settings.get("auto_send_only_safe", True)):
        should_send = should_send and safe

    ok, action = paste_reply(driver, reply, send=should_send)

    print("-" * 94)
    print("RELANCE AUTO :", chat_title)
    print("Action :", action)
    print(reply)

    remember_outgoing(chat_title, reply, follow.get("intent", "auto_followup"), should_send and ok)

    return True

def main():
    global LAST_CHAT_TITLE

    s = load_settings()

    print("=" * 94)
    print("FASTBOT WhatsApp — V8.1 Autonomous Sales Runtime")
    print("=" * 94)
    print("Admin :", "admin_control_gui.bat")
    print("Mode envoi :", "AUTO" if s.get("send_automatically") else "SÉCURISÉ")
    print("Autonomie :", bool(s.get("autonomous_mode_enabled", False)))
    print("Scan non-lus :", bool(s.get("auto_scan_unread_chats", False)))
    print("Relances :", bool(s.get("auto_followup_enabled", False)))
    print("=" * 94)

    driver = attach_driver()
    ensure_whatsapp_tab(driver)
    wait_for_whatsapp_ready(driver)

    while True:
        try:
            s = load_settings()
            chat_title = get_chat_title(driver)

            if bool(s.get("skip_conversation_ouverte", True)) and chat_title == "conversation_ouverte":
                if patrol_next_chat(driver, s):
                    time.sleep(float(s.get("auto_scan_when_idle_seconds", 4)))
                    continue
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            chat_changed = chat_title != LAST_CHAT_TITLE
            if chat_changed:
                print("")
                print("➡️ Conversation active :", chat_title)
                LAST_CHAT_TITLE = chat_title

            if bool(s.get("audit_all_visible_messages", True)):
                rows = audit_chat_messages(driver, chat_title)
                print_audit_rows(rows)

            precheck = smart_campaign_precheck(driver, chat_title, chat_changed)
            state = get_state(chat_title)

            if state.get("needs_campaign_label"):
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            recent_messages = get_actionable_incoming_messages(driver, chat_title, limit=55)

            if not recent_messages:
                handle_followup(driver, chat_title, s)

                if patrol_next_chat(driver, s):
                    time.sleep(float(s.get("auto_scan_when_idle_seconds", 4)))
                    continue

                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            combined_msg = "\n".join(recent_messages)
            last_msg = recent_messages[-1]
            context_key = str(state.get("campaign_id", "")) + "|" + str(state.get("last_category", ""))

            if already_handled(chat_title, combined_msg, context_key):
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            remember_incoming(chat_title, recent_messages)

            result = decide_reply(combined_msg, last_msg, chat_title)

            try:
                state_patch = result.get("_state_patch") or {}
                if state_patch:
                    set_state(chat_title, state_patch)
                    state.update(state_patch)
            except Exception as mem_err:
                print("Erreur mémoire conversation :", repr(mem_err))

            reply = result.get("reply", "").strip()
            conf = float(result.get("confidence", 0))
            intent = result.get("intent", "")
            safe = bool(result.get("safe_to_auto_send", False))

            should_send = bool(s.get("send_automatically", False)) and conf >= float(s.get("confidence_required", 0.88))
            if bool(s.get("auto_send_only_safe", True)):
                should_send = should_send and safe

            print("-" * 94)
            print("Conversation :", chat_title)
            print("Précheck :", precheck)
            print("Contexte :", state.get("campaign_label", state.get("last_category", "aucun")))
            print("Messages analysés :")
            for i, m in enumerate(recent_messages, 1):
                print(f"{i}. {m}")
            print("Intent :", intent, "| confiance :", conf, "| safe :", safe)
            print("Auto-send :", should_send)

            action = "no_reply"
            ok = False
            media_result = {"sent": 0, "error": ""}

            if reply and conf >= 0.35:
                ok, action = paste_reply(driver, reply, send=should_send)
                print("Action :", action)
                print("Réponse :")
                print(reply)

                if ok and should_send and not result.get("_no_media"):
                    media_result = maybe_send_media(driver, combined_msg, chat_title, result, should_send)
            else:
                print("Silence / aucune réponse utile.")

            row = {
                "chat": chat_title,
                "precheck": precheck,
                "campaign_label": state.get("campaign_label", ""),
                "campaign_category": state.get("campaign_category", ""),
                "client_messages": recent_messages,
                "reply": reply,
                "intent": intent,
                "confidence": conf,
                "safe": safe,
                "auto_sent": should_send and ok,
                "pasted": ok,
                "action": action,
                "media": media_result,
                "state_patch": result.get("_state_patch", {}),
                "debug": result.get("debug", {})
            }

            log_event(row)
            log_decision(row)
            remember_outgoing(chat_title, reply, intent, should_send and ok)
            mark_handled(chat_title, combined_msg, intent, action, context_key)

            time.sleep(float(s.get("poll_seconds", 1.5)))

        except KeyboardInterrupt:
            print("\nArrêt demandé.")
            break
        except Exception as e:
            if e.__class__.__name__ == "InvalidSessionIdException":
                print("Session Chrome perdue. Ferme Chrome contrôlé puis relance .\\start_bot.bat")
                log_event({"error": repr(e), "where": "main_loop", "fatal": True})
                break

            print("Erreur capturée, le bot continue :", repr(e))
            log_event({"error": repr(e), "where": "main_loop"})
            time.sleep(3)

if __name__ == "__main__":
    main()
