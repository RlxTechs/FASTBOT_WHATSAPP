import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image
from selenium.webdriver.common.by import By

from app_paths import BASE_DIR
CAMPAIGNS_PATH = BASE_DIR / "campaigns.json"
UNKNOWN_PATH = BASE_DIR / "unknown_campaigns.json"
CAPTURES_DIR = BASE_DIR / "campaign_captures"
CAPTURES_DIR.mkdir(exist_ok=True)

FACEBOOK_MARKERS = [
    "publicite de facebook",
    "publicité de facebook",
    "afficher les details",
    "afficher les détails",
    "salutation automatique",
    "comment pouvons nous vous aider",
    "comment pouvons-nous vous aider",
    "dites nous comment nous pouvons vous aider",
    "dites-nous comment nous pouvons vous aider"
]

def load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def normalize(text: str) -> str:
    import unicodedata
    text = str(text or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9+\s'.:/-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def campaigns_data() -> Dict[str, Any]:
    return load_json(CAMPAIGNS_PATH, {"version": 1, "match_threshold": 10, "campaigns": []})

def unknown_data() -> Dict[str, Any]:
    return load_json(UNKNOWN_PATH, {"unknown": {}})

def average_hash_from_png(png_bytes: bytes, hash_size: int = 8) -> str:
    img = Image.open(io.BytesIO(png_bytes)).convert("L")
    try:
        resample = Image.Resampling.LANCZOS
    except Exception:
        resample = Image.LANCZOS
    img = img.resize((hash_size, hash_size), resample)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p > avg else "0" for p in pixels)
    return hex(int(bits, 2))[2:].zfill(hash_size * hash_size // 4)

def text_hash(text: str) -> str:
    return hashlib.sha1(normalize(text).encode("utf-8")).hexdigest()[:16]

def hamming(a: str, b: str) -> int:
    try:
        x = int(a, 16) ^ int(b, 16)
        return bin(x).count("1")
    except Exception:
        return 999

def is_facebook_ad_text(text: str) -> bool:
    t = normalize(text)
    return any(normalize(m) in t for m in FACEBOOK_MARKERS)

def recent_bubbles(driver, limit: int = 40):
    bubbles = driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
    return bubbles[-limit:]

def find_facebook_ad_cards(driver, limit: int = 40):
    cards = []
    for bubble in recent_bubbles(driver, limit):
        try:
            txt = bubble.text.strip()
        except Exception:
            txt = ""
        if is_facebook_ad_text(txt):
            cards.append((bubble, txt))
    return cards

def element_png(el) -> bytes:
    try:
        png = el.screenshot_as_png
        if png and len(png) > 300:
            return png
    except Exception:
        pass
    return b""

def best_thumbnail_or_card_png(bubble) -> bytes:
    candidates = []

    try:
        imgs = bubble.find_elements(By.CSS_SELECTOR, "img")
    except Exception:
        imgs = []

    for img in imgs:
        try:
            size = img.size or {}
            w = int(size.get("width", 0))
            h = int(size.get("height", 0))

            if w < 20 or h < 20:
                continue

            png = element_png(img)
            if png:
                candidates.append((w * h, png, "img"))
        except Exception:
            continue

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    # Secours : si la vraie miniature n’est pas accessible, on screenshot toute la carte.
    return element_png(bubble)

def find_campaign_by_hash(ahash: str) -> Optional[Dict[str, Any]]:
    data = campaigns_data()
    threshold = int(data.get("match_threshold", 10))

    best = None
    best_dist = 999

    for c in data.get("campaigns", []):
        for h in c.get("hashes", []) or []:
            dist = hamming(ahash, h)
            if dist < best_dist:
                best_dist = dist
                best = c

    if best and best_dist <= threshold:
        found = dict(best)
        found["_match_distance"] = best_dist
        found["_match_type"] = "image_hash"
        return found

    return None

def find_campaign_by_keywords(text: str) -> Optional[Dict[str, Any]]:
    t = normalize(text)

    # Attention : les salutations automatiques Facebook sont souvent génériques.
    # On n'utilise les mots-clés que si le texte contient vraiment des mots produits.
    best = None
    best_score = 0

    for c in campaigns_data().get("campaigns", []):
        score = 0
        for kw in c.get("keywords", []) or []:
            kn = normalize(kw)
            if kn and kn in t:
                score += 1
        if score > best_score:
            best_score = score
            best = c

    if best and best_score >= 2:
        found = dict(best)
        found["_match_type"] = "card_text_keywords"
        found["_match_text_score"] = best_score
        return found

    return None

def campaign_state_patch(c: Dict[str, Any]) -> Dict[str, Any]:
    patch = {
        "needs_campaign_label": False,
        "campaign_id": c.get("id", ""),
        "campaign_label": c.get("label", ""),
        "campaign_category": c.get("category", ""),
        "campaign_intent": c.get("intent", ""),
        "campaign_product_id": c.get("product_id", ""),
        "campaign_product_query": c.get("product_query", ""),
        "last_category": c.get("category", "")
    }
    if c.get("product_id"):
        patch["last_product_id"] = c.get("product_id")
    return patch

def save_unknown_card(card_id: str, png: bytes, chat_id: str, card_text: str, source: str):
    data = unknown_data()
    unknown = data.setdefault("unknown", {})

    img_path = ""
    if png:
        p = CAPTURES_DIR / f"unknown_{card_id}.png"
        if not p.exists():
            p.write_bytes(png)
        img_path = str(p)

    if card_id not in unknown:
        unknown[card_id] = {
            "hash": card_id,
            "image": img_path,
            "chat_example": chat_id,
            "card_text": card_text,
            "label_status": "waiting_label",
            "source": source,
            "note": "Carte Facebook détectée. Attribue-la dans l'admin graphique."
        }
    else:
        if img_path:
            unknown[card_id]["image"] = img_path
        unknown[card_id]["last_chat_example"] = chat_id
        unknown[card_id]["card_text"] = card_text

    save_json(UNKNOWN_PATH, data)

def detect_campaign_from_chat(driver, chat_id: str = "conversation") -> Optional[Dict[str, Any]]:
    cards = find_facebook_ad_cards(driver)

    if cards:
        print(f"[PRECHECK] Cartes Facebook détectées : {len(cards)}")

    for bubble, card_text in reversed(cards):
        png = best_thumbnail_or_card_png(bubble)
        card_id = ""

        if png:
            try:
                card_id = average_hash_from_png(png)
            except Exception:
                card_id = ""

        if not card_id:
            card_id = text_hash(card_text)

        if png:
            campaign = find_campaign_by_hash(card_id)
            if campaign:
                return {
                    "source": "facebook_ad_card_image_hash",
                    "hash": card_id,
                    "label": campaign.get("label"),
                    "campaign": campaign,
                    "state_patch": campaign_state_patch(campaign),
                    "unknown": False
                }

        campaign = find_campaign_by_keywords(card_text)
        if campaign:
            return {
                "source": "facebook_ad_card_text_keywords",
                "hash": card_id,
                "label": campaign.get("label"),
                "campaign": campaign,
                "state_patch": campaign_state_patch(campaign),
                "unknown": False
            }

        save_unknown_card(card_id, png, chat_id, card_text, "facebook_ad_card_unknown")

        return {
            "source": "facebook_ad_card_unknown",
            "unknown": True,
            "hash": card_id,
            "label": "Pub Facebook inconnue",
            "state_patch": {},
            "card_text": card_text
        }

    return None
