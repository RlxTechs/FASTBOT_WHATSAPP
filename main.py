import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

import pyperclip
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from chrome_control import attach_driver, ensure_whatsapp_tab, wait_for_whatsapp_ready
from bot_core import get_state, set_state
from campaign_context import detect_campaign_from_chat
from conversation_brain import generate_human_sales_reply
from sales_safety_filters import classify_pre_reply
from runtime_priority_rules import try_priority_reply
from conversation_guard import clean_recent_messages
from runtime_message_reader import get_actionable_incoming_messages
from message_audit import audit_chat_messages, print_audit_rows
from auto_inbox import open_next_unread_chat

try:
    from media_engine import select_media_for_reply, send_media_files
except Exception:
    select_media_for_reply = None
    send_media_files = None

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "conversations_log.jsonl"
BOT_DECISIONS = BASE_DIR / "bot_decisions.jsonl"
SETTINGS_PATH = BASE_DIR / "settings.json"
FORCE_RESCAN_FLAG = BASE_DIR / "force_precheck.flag"
HANDLED_PATH = BASE_DIR / "handled_incoming.json"

PRECHECK_CACHE = {}
LAST_CHAT_TITLE = None

def load_settings():
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        data = {}

    defaults = {
        "send_automatically": False,
        "autonomous_mode_enabled": False,
        "auto_scan_unread_chats": False,
        "auto_scan_when_idle_seconds": 4,
        "audit_all_visible_messages": True,
        "confidence_required": 0.88,
        "auto_send_only_safe": True,
        "skip_if_message_box_not_empty": True,
        "auto_send_delay_seconds": 0.6,
        "poll_seconds": 1.5,
        "precheck_verbose": False,
        "precheck_fast_retry_count": 1,
        "precheck_retry_fast_seconds": 4,
        "precheck_rescan_after_seconds": 180,
        "precheck_rescan_known_after_seconds": 3600,
        "precheck_wait_after_chat_change_seconds": 1.0,
        "skip_conversation_ouverte": True
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

def message_fingerprint(chat_title, combined_msg, context=""):
    raw = f"{chat_title}::{context}::{combined_msg.strip()}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:24]

def already_handled(chat_title, combined_msg, context=""):
    data = load_handled()
    return message_fingerprint(chat_title, combined_msg, context) in data

def mark_handled(chat_title, combined_msg, intent, action, context=""):
    data = load_handled()
    key = message_fingerprint(chat_title, combined_msg, context)
    data[key] = {
        "chat": chat_title,
        "message": combined_msg,
        "intent": intent,
        "action": action,
        "context": context,
        "time": datetime.now().isoformat(timespec="seconds")
    }

    if len(data) > 1000:
        keys = list(data.keys())[-1000:]
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

def clean_message_text(text):
    lines = []
    for line in (text or "").splitlines():
        t = line.strip()
        if not t:
            continue
        if len(t) <= 5 and ":" in t and any(ch.isdigit() for ch in t):
            continue
        if t.lower() in {"modifié", "edited"}:
            continue
        lines.append(t)
    return "\n".join(lines).strip()

def read_unanswered_incoming_messages(driver, limit=14):
    messages = []
    try:
        bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
        if not bubbles:
            return []

        tail = bubbles[-limit:]

        last_out_index = -1
        for i, b in enumerate(tail):
            try:
                cls = b.get_attribute("class") or ""
                if "message-out" in cls:
                    last_out_index = i
            except Exception:
                pass

        candidates = tail[last_out_index + 1:] if last_out_index >= 0 else tail[-4:]

        for bubble in candidates:
            try:
                cls = bubble.get_attribute("class") or ""
                if "message-in" not in cls:
                    continue

                spans = bubble.find_elements(By.CSS_SELECTOR, "span.selectable-text.copyable-text")
                parts = []
                for s_el in spans:
                    try:
                        tx = s_el.text.strip()
                        if tx:
                            parts.append(tx)
                    except StaleElementReferenceException:
                        continue

                txt = clean_message_text("\n".join(parts)) if parts else clean_message_text(bubble.text)
                if txt:
                    messages.append(txt)
            except Exception:
                continue
    except Exception:
        return []

    clean = []
    for m in messages:
        if m and m not in clean:
            clean.append(m)

    return clean

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

    current_draft = get_box_text(box)
    if settings.get("skip_if_message_box_not_empty", True) and current_draft:
        return False, "brouillon_deja_present_non_ecrase"

    box.click()
    time.sleep(0.1)
    box.send_keys(Keys.CONTROL, "a")
    time.sleep(0.05)
    box.send_keys(Keys.BACKSPACE)
    time.sleep(0.05)

    pyperclip.copy(reply_text)
    box.send_keys(Keys.CONTROL, "v")
    time.sleep(float(settings.get("auto_send_delay_seconds", 0.6)))

    if send:
        box.send_keys(Keys.ENTER)

    return True, "envoye" if send else "colle"

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

    if state.get("needs_campaign_label"):
        return False, "waiting_admin_label"

    if chat_changed:
        return True, "chat_changed_force_scan"

    if chat_title not in PRECHECK_CACHE:
        return True, "first_time_chat"

    if not state.get("campaign_id"):
        last_scan = float(cache.get("last_scan", 0))
        attempts = int(cache.get("no_context_attempts", 0))
        fast_count = int(settings.get("precheck_fast_retry_count", 1))

        if attempts < fast_count and now_ts - last_scan >= float(settings.get("precheck_retry_fast_seconds", 4)):
            return True, "no_context_fast_retry"

        if now_ts - last_scan >= float(settings.get("precheck_rescan_after_seconds", 180)):
            return True, "no_context_slow_retry"

        return False, "no_context_cached"

    last_scan = float(cache.get("last_scan", 0))
    if now_ts - last_scan >= float(settings.get("precheck_rescan_known_after_seconds", 3600)):
        return True, "known_context_periodic_rescan"

    return False, "known_context_cached"

def update_cache(chat_title, status, extra=None):
    old = PRECHECK_CACHE.get(chat_title, {})
    data = {
        "last_scan": time.time(),
        "status": status,
        "no_context_attempts": old.get("no_context_attempts", 0)
    }
    if extra:
        data.update(extra)
    PRECHECK_CACHE[chat_title] = data

def smart_campaign_precheck(driver, chat_title, chat_changed):
    settings = load_settings()
    verbose = bool(settings.get("precheck_verbose", False))

    do_scan, reason = should_precheck(chat_title, chat_changed)
    if not do_scan:
        return reason

    if reason == "chat_changed_force_scan":
        time.sleep(float(settings.get("precheck_wait_after_chat_change_seconds", 1.0)))

    try:
        camp = detect_campaign_from_chat(driver, chat_title)
    except Exception as e:
        update_cache(chat_title, "precheck_error", {"error": repr(e)})
        if e.__class__.__name__ == "InvalidSessionIdException":
            raise
        if verbose:
            print("[PRECHECK] Erreur analyse Facebook :", repr(e))
        return "precheck_error"

    state_before = get_state(chat_title)

    if not camp:
        old = PRECHECK_CACHE.get(chat_title, {})
        attempts = int(old.get("no_context_attempts", 0)) + 1
        update_cache(chat_title, "no_campaign_card", {"no_context_attempts": attempts})

        if state_before.get("campaign_id") and not state_before.get("needs_campaign_label"):
            if verbose:
                print("[PRECHECK] Carte non visible, contexte conservé :", state_before.get("campaign_label"))
            return "known_context_preserved"

        if verbose:
            print("[PRECHECK] Aucune carte Facebook détectée. Tentative :", attempts, "| raison :", reason)
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

        update_cache(chat_title, "unknown_campaign_logged", {"hash": h, "no_context_attempts": 0})

        if block_unknown:
            print("⚠️ Pub inconnue détectée. Conversation bloquée en attente admin. Hash :", h)
            return "unknown_campaign_blocked"

        print("⚠️ Pub inconnue détectée mais conversation NON bloquée. Hash :", h)
        return "unknown_campaign_logged_continue"

    patch = camp.get("state_patch", {})
    patch["needs_campaign_label"] = False
    set_state(chat_title, patch)

    update_cache(chat_title, "campaign_detected", {
        "campaign_label": camp.get("label"),
        "source": camp.get("source"),
        "no_context_attempts": 0
    })

    if verbose or reason == "chat_changed_force_scan":
        print("[PRECHECK] Contexte pub détecté/confirmé :", camp.get("label"), "| source :", camp.get("source"), "| raison :", reason)

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

        print("Mode non-auto : médias non envoyés automatiquement.")
        return {"sent": 0, "error": "auto_send_disabled"}
    except Exception as e:
        print("Erreur médias :", repr(e))
        return {"sent": 0, "error": repr(e)}

def main():
    global LAST_CHAT_TITLE

    s = load_settings()
    send_auto = bool(s.get("send_automatically", False))
    min_conf = float(s.get("confidence_required", 0.88))
    safe_only = bool(s.get("auto_send_only_safe", True))

    print("=" * 94)
    print("FASTBOT WhatsApp — V7 PRO Runtime")
    print("=" * 94)
    print("Logs : audit_messages.jsonl + bot_decisions.jsonl + conversations_log.jsonl")
    print("Admin autonomie : admin_control_gui.bat")
    print("Mode :", "AUTO" if send_auto else "SÉCURISÉ : colle sans envoyer")
    print("Autonomie :", bool(s.get("autonomous_mode_enabled", False)))
    print("=" * 94)

    driver = attach_driver()
    ensure_whatsapp_tab(driver)
    wait_for_whatsapp_ready(driver)

    while True:
        try:
            s = load_settings()

            chat_title = get_chat_title(driver)

            if bool(s.get("skip_conversation_ouverte", True)) and chat_title == "conversation_ouverte":
                if bool(s.get("autonomous_mode_enabled", False)) and bool(s.get("auto_scan_unread_chats", False)):
                    open_next_unread_chat(driver)
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            chat_changed = chat_title != LAST_CHAT_TITLE
            if chat_changed:
                print("")
                print("➡️ Nouvelle conversation active :", chat_title)
                LAST_CHAT_TITLE = chat_title

            if bool(s.get("audit_all_visible_messages", True)):
                audit_rows = audit_chat_messages(driver, chat_title)
                print_audit_rows(audit_rows)

            precheck = smart_campaign_precheck(driver, chat_title, chat_changed)
            state = get_state(chat_title)

            if state.get("needs_campaign_label"):
                time.sleep(float(s.get("poll_seconds", 1.5)))
                continue

            recent_messages = get_actionable_incoming_messages(driver, chat_title, limit=45)

            if not recent_messages:
                if bool(s.get("autonomous_mode_enabled", False)) and bool(s.get("auto_scan_unread_chats", False)):
                    opened = open_next_unread_chat(driver)
                    if opened:
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

            priority = try_priority_reply(combined_msg, last_msg, chat_title)
            if priority:
                result = priority
            else:
                pre_filter = classify_pre_reply(combined_msg, last_msg, chat_title)
                if pre_filter:
                    result = pre_filter
                else:
                    result = generate_human_sales_reply(combined_msg, chat_title)

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
            print("Messages client analysés :")
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
