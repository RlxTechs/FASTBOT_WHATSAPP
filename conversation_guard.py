import json
from datetime import datetime
from pathlib import Path
from bot_core import normalize

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

CORRECTIONS_LOG = BASE_DIR / "human_corrections.jsonl"

def log_correction(chat_id: str, text: str, reason: str):
    try:
        row = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "chat": chat_id,
            "text": text,
            "reason": reason
        }
        with CORRECTIONS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass

def is_deleted_marker(text: str) -> bool:
    m = normalize(text)
    return (
        "vous avez supprime ce message" in m
        or "vous avez supprimé ce message" in m
        or "ce message a ete supprime" in m
        or "ce message a été supprimé" in m
        or "message supprime" in m
        or "message supprimé" in m
    )

def is_system_noise(text: str) -> bool:
    m = normalize(text)
    noises = [
        "appel vocal manque",
        "appel vocal manqué",
        "rappelez des personnes sur votre telephone",
        "rappelez des personnes sur votre téléphone",
        "messages et appels sont chiffres",
        "message transfere",
        "message transféré",
        "transfere",
        "transféré"
    ]
    return any(x in m for x in noises)

def is_my_visible_message(text: str) -> bool:
    raw = (text or "").strip()
    m = normalize(raw)

    if raw.startswith("Vous\n") or raw.startswith("Vous\r\n"):
        return True

    if m.startswith("vous ") and len(m.split()) > 2:
        return True

    return False

def is_ack_or_note(text: str) -> bool:
    m = normalize(text)

    if not m:
        return True

    if "j ai pris note" in m or "j'ai pris note" in m:
        return True

    if len(m.split()) > 6:
        return False

    exact = {
        "ok", "okay", "d accord", "daccord", "d'accord",
        "merci", "merci bien", "merci beaucoup",
        "bien recu", "bien reçu", "recu", "reçu",
        "note", "noté", "c est bon", "cest bon",
        "ca marche", "ça marche", "parfait", "cool",
        "oui", "non merci", "daccord merci"
    }

    return m in exact

def is_generic_fb_greeting(text: str) -> bool:
    m = normalize(text)
    return (
        "bonjour puis je en savoir plus" in m
        or "puis je en savoir plus a ce sujet" in m
        or "puis je en savoir plus à ce sujet" in m
        or "en savoir plus a ce sujet" in m
        or "en savoir plus à ce sujet" in m
    )

def is_simple_greeting(text: str) -> bool:
    m = normalize(text)
    return m in {"cc", "bonjour", "bonsoir", "bjr", "bsr", "salut", "slt", "hello", "coucou"}

def clean_recent_messages(messages, chat_id: str = "default"):
    cleaned = []

    for msg in messages or []:
        t = (msg or "").strip()
        if not t:
            continue

        if is_deleted_marker(t):
            log_correction(chat_id, t, "deleted_message_visible")
            continue

        if is_my_visible_message(t):
            log_correction(chat_id, t, "outgoing_message_seen")
            continue

        if is_system_noise(t):
            log_correction(chat_id, t, "system_noise_ignored")
            continue

        cleaned.append(t)

    if not cleaned:
        return []

    latest = cleaned[-1]

    # Si le dernier message du client est juste “ok/d’accord/merci”, silence total.
    if is_ack_or_note(latest):
        log_correction(chat_id, latest, "latest_ack_no_reply")
        return []

    # Si le client a envoyé une vraie précision après le message Facebook générique, on retire l'ancien générique.
    if len(cleaned) > 1:
        last_norm = normalize(cleaned[-1])
        cleaned = [
            m for m in cleaned
            if not (is_generic_fb_greeting(m) and normalize(m) != last_norm)
        ]

    # Si un vrai message suit “bonjour”, on retire “bonjour”.
    if len(cleaned) > 1:
        cleaned = [m for m in cleaned if not is_simple_greeting(m)]

    return cleaned[-4:]
