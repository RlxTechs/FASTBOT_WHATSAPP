import re
from selenium.webdriver.common.by import By
from conversation_guard import clean_recent_messages

def clean_message_text(text):
    lines = []
    for line in (text or "").splitlines():
        t = line.strip()
        if not t:
            continue
        if re.fullmatch(r"\d{1,2}:\d{2}", t):
            continue
        if t.lower() in {"modifié", "edited"}:
            continue
        lines.append(t)
    return "\n".join(lines).strip()

def extract_text_from_bubble(bubble):
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
        return clean_message_text("\n".join(parts))

    try:
        return clean_message_text(bubble.text)
    except Exception:
        return ""

def is_auto_greeting_or_ad_card(text):
    low = (text or "").lower()
    checks = [
        "publicité de facebook",
        "publicite de facebook",
        "afficher les détails",
        "afficher les details",
        "salutation automatique",
        "bonjour ! dites-nous comment nous pouvons vous aider",
        "bonjour ! dites nous comment nous pouvons vous aider"
    ]
    return any(x in low for x in checks)

def is_pending_encryption_message(text):
    low = (text or "").lower()
    return (
        "en attente de ce message" in low
        or "vérifiez votre téléphone" in low
        or "verifiez votre telephone" in low
    )

def is_real_outgoing_message(text):
    if not text:
        return False

    if is_auto_greeting_or_ad_card(text):
        return False

    if is_pending_encryption_message(text):
        return False

    return True

def strip_whatsapp_reply_quote(text):
    """
    Quand WhatsApp affiche :
    Vous
    Ancien message cité
    Nouveau message client

    On garde surtout le dernier vrai message client.
    """
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    if not lines:
        return ""

    if lines[0].lower() == "vous" and len(lines) >= 3:
        return lines[-1].strip()

    return "\n".join(lines).strip()

def get_actionable_incoming_messages(driver, chat_title, limit=45):
    """
    Lit les vrais messages clients à traiter.

    Correction importante :
    - une salutation automatique Facebook/WhatsApp ne bloque plus la réponse ;
    - les cartes Publicité Facebook ne comptent plus comme vraie réponse sortante ;
    - les messages 'En attente de ce message' sont ignorés ;
    - les citations WhatsApp 'Vous / ancien message / nouveau message' sont nettoyées.
    """
    rows = []

    try:
        bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    except Exception:
        return []

    for bubble in bubbles[-limit:]:
        try:
            cls = bubble.get_attribute("class") or ""
            direction = "outgoing" if "message-out" in cls else "incoming"
            text = extract_text_from_bubble(bubble)

            if not text:
                continue

            rows.append({
                "direction": direction,
                "text": text,
                "auto_greeting": is_auto_greeting_or_ad_card(text),
                "pending": is_pending_encryption_message(text)
            })
        except Exception:
            continue

    if not rows:
        return []

    # Dernier vrai message sortant = réponse humaine/bot réelle.
    # Les salutations automatiques Facebook ne comptent pas.
    last_real_out = -1
    for i, row in enumerate(rows):
        if row["direction"] == "outgoing" and is_real_outgoing_message(row["text"]):
            last_real_out = i

    candidates = rows[last_real_out + 1:] if last_real_out >= 0 else rows[-8:]

    incoming = []
    for row in candidates:
        if row["direction"] != "incoming":
            continue

        text = row["text"]

        if row.get("pending"):
            continue

        text = strip_whatsapp_reply_quote(text)

        if text:
            incoming.append(text)

    # Nettoyage final déjà existant : supprime ok/d'accord, supprimé, bruit, etc.
    return clean_recent_messages(incoming, chat_title)
