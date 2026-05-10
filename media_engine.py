import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bot_core import normalize, get_state

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

MEDIA_PATH = BASE_DIR / "media_catalog.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

GENERIC_INTENT_BLOCKLIST = {
    "seller_fallback_no_context",
    "sales_no_thumbnail_facebook_fallback",
    "sales_catalog_overview",
    "food_open_today_human",
    "food_order_today_human",
    "sales_opening_hours",
    "sales_location_by_category",
    "non_food_location",
    "non_food_delivery",
    "hr_not_hiring",
    "no_reply_acknowledgement",
    "unknown_facebook_campaign_waiting_admin",
    "waiting_facebook_campaign_context"
}

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def save_json(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def media_data() -> Dict[str, Any]:
    data = load_json(MEDIA_PATH, {})
    if not data:
        data = {
            "version": "6.2",
            "enabled": True,
            "send_images_automatically": True,
            "max_images_per_reply": 3,
            "strict_mode": True,
            "bundles": []
        }
        save_json(MEDIA_PATH, data)
    data.setdefault("enabled", True)
    data.setdefault("send_images_automatically", True)
    data.setdefault("max_images_per_reply", 3)
    data.setdefault("strict_mode", True)
    data.setdefault("bundles", [])
    return data

def clean_path(p: str) -> str:
    p = str(p or "").strip()
    if p.startswith("./"):
        p = p[2:]
    return p.replace("\\", "/")

def abs_existing_image(p: str) -> str:
    p = clean_path(p)
    if not p:
        return ""
    full = Path(p)
    if not full.is_absolute():
        full = BASE_DIR / p
    if full.exists() and full.is_file() and full.suffix.lower() in IMAGE_EXTS:
        return str(full.resolve())
    return ""

def existing_images(paths: List[str]) -> List[str]:
    out = []
    for p in paths or []:
        img = abs_existing_image(p)
        if img and img not in out:
            out.append(img)
    return out

def split_terms(value) -> List[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value or "").replace("\n", ",").split(",")
    return [str(x).strip() for x in raw if str(x).strip()]

def contains_any(text_norm: str, terms: List[str]) -> bool:
    for t in terms:
        tn = normalize(t)
        if tn and tn in text_norm:
            return True
    return False

def bundle_score(bundle: Dict[str, Any], message: str, chat_id: str, result: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    V6.2 strict :
    - On ne scanne PLUS la réponse du bot pour déclencher des images.
    - Le message CLIENT doit contenir un mot-clé direct, sauf si le résultat demande explicitement un bundle.
    - Le contexte seul ne suffit pas, sauf allow_context_only=true dans admin.
    """
    reasons = []

    if not bundle.get("active", True):
        return -999, ["inactive"]

    intent = str(result.get("intent", ""))
    message_norm = normalize(message)
    state = get_state(chat_id)

    bundle_ids_requested = result.get("_media_bundle_ids") or []
    if bundle.get("id") in bundle_ids_requested:
        reasons.append("explicit_result_bundle")
        return 100, reasons

    negative_keywords = split_terms(bundle.get("negative_keywords", []))
    if negative_keywords and contains_any(message_norm, negative_keywords):
        return -999, ["negative_keyword"]

    keywords = split_terms(bundle.get("keywords", []))
    keyword_hits = []
    for kw in keywords:
        kn = normalize(kw)
        if kn and kn in message_norm:
            keyword_hits.append(kw)

    score = 0

    if keyword_hits:
        score += 20 + (len(keyword_hits) * 3)
        reasons.append("keyword:" + ", ".join(keyword_hits[:5]))

    # Contextes : ajout faible uniquement si mot-clé déjà trouvé OU allow_context_only=true
    contexts = split_terms(bundle.get("contexts", []))
    allow_context_only = bool(bundle.get("allow_context_only", False))
    state_text = normalize(" ".join([
        str(state.get("campaign_id", "")),
        str(state.get("campaign_category", "")),
        str(state.get("last_category", "")),
        str(state.get("campaign_label", "")),
        str(state.get("last_product_family", "")),
        str(state.get("last_product_query", "")),
        str(state.get("campaign_product_query", ""))
    ]))

    context_hit = []
    for ctx in contexts:
        cn = normalize(ctx)
        if cn and cn in state_text:
            context_hit.append(ctx)

    if context_hit and (keyword_hits or allow_context_only):
        score += 5
        reasons.append("context:" + ", ".join(context_hit[:3]))

    # Intent : seulement si le bundle a été configuré pour cet intent.
    intents = split_terms(bundle.get("intents", []))
    if intent and intent in intents and (keyword_hits or bool(bundle.get("allow_intent_only", False))):
        score += 10
        reasons.append("intent:" + intent)

    try:
        score += int(bundle.get("priority", 0))
    except Exception:
        pass

    try:
        min_score = int(bundle.get("min_score", 15))
    except Exception:
        min_score = 15

    if score < min_score:
        return -1, reasons + [f"score_below_min:{score}<{min_score}"]

    return score, reasons

def direct_product_images_from_result(result: Dict[str, Any]) -> List[str]:
    """
    Les images venant de products.json sont prioritaires.
    Elles sont acceptées même si l'intent est générique seulement si le résultat les donne explicitement.
    """
    direct = result.get("_media_images") or []
    return existing_images(direct)

def select_media_for_reply(message: str, chat_id: str, result: Dict[str, Any]) -> List[str]:
    data = media_data()

    if not data.get("enabled", True):
        return []

    if result.get("_no_media") is True:
        return []

    intent = str(result.get("intent", ""))

    # 1) Priorité absolue : images explicites venues de products.json ou d'une règle produit.
    direct = direct_product_images_from_result(result)
    if direct:
        return direct[: int(data.get("max_images_per_reply", 3))]

    # 2) Pour les réponses générales/fallback, aucune image automatique.
    if intent in GENERIC_INTENT_BLOCKLIST:
        return []

    # 3) Si envoi auto désactivé dans config admin.
    if not data.get("send_images_automatically", True):
        return []

    scored = []
    for bundle in data.get("bundles", []) or []:
        imgs = existing_images(bundle.get("image_paths", []))
        if not imgs:
            continue

        score, reasons = bundle_score(bundle, message, chat_id, result)
        if score > 0:
            scored.append((score, bundle, imgs, reasons))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0], reverse=True)

    selected = []
    global_max = int(data.get("max_images_per_reply", 3))

    for score, bundle, imgs, reasons in scored:
        try:
            local_max = int(bundle.get("max_images", global_max))
        except Exception:
            local_max = global_max

        for img in imgs[:local_max]:
            if img not in selected:
                selected.append(img)
            if len(selected) >= global_max:
                return selected

    return selected[:global_max]

def explain_media_selection(message: str, chat_id: str, result: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = media_data()
    rows = []

    direct = direct_product_images_from_result(result)
    if direct:
        rows.append({
            "type": "products_json_direct",
            "score": 999,
            "images": direct,
            "reason": "result._media_images"
        })

    for bundle in data.get("bundles", []) or []:
        imgs = existing_images(bundle.get("image_paths", []))
        score, reasons = bundle_score(bundle, message, chat_id, result)
        rows.append({
            "id": bundle.get("id"),
            "label": bundle.get("label"),
            "active": bundle.get("active", True),
            "score": score,
            "reasons": reasons,
            "images_found": len(imgs),
            "images": imgs
        })

    rows.sort(key=lambda x: int(x.get("score", -999)), reverse=True)
    return rows

def find_file_input(driver):
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
    for inp in inputs:
        return inp
    return None

def click_attach_button(driver):
    selectors = [
        "span[data-icon='plus']",
        "span[data-icon='clip']",
        "div[title='Joindre']",
        "div[title='Attach']",
        "button[title='Attach']",
        "button[aria-label='Attach']",
        "button[aria-label='Joindre']"
    ]
    for css in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, css)
            for el in els:
                if el.is_displayed():
                    el.click()
                    time.sleep(0.5)
                    return True
        except Exception:
            continue
    return False

def send_media_files(driver, image_paths: List[str], caption: str = "") -> Dict[str, Any]:
    if not image_paths:
        return {"sent": 0, "error": ""}

    sent = 0
    errors = []

    for img in image_paths:
        try:
            if not Path(img).exists():
                errors.append("image_missing:" + img)
                continue

            click_attach_button(driver)
            time.sleep(0.5)

            file_input = find_file_input(driver)
            if not file_input:
                errors.append("input_file_introuvable")
                continue

            file_input.send_keys(img)
            time.sleep(1.5)

            if caption:
                try:
                    boxes = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")
                    if boxes:
                        boxes[-1].click()
                        boxes[-1].send_keys(caption)
                except Exception:
                    pass

            sent_ok = False
            send_selectors = [
                "span[data-icon='send']",
                "span[data-icon='wds-ic-send-filled']",
                "button[aria-label='Envoyer']",
                "button[aria-label='Send']"
            ]
            for css in send_selectors:
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, css)
                    for btn in btns:
                        if btn.is_displayed():
                            btn.click()
                            sent += 1
                            sent_ok = True
                            time.sleep(1.0)
                            break
                    if sent_ok:
                        break
                except Exception:
                    continue

            if not sent_ok:
                try:
                    boxes = driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")
                    if boxes:
                        boxes[-1].send_keys(Keys.ENTER)
                        sent += 1
                        time.sleep(1.0)
                    else:
                        errors.append("bouton_send_introuvable")
                except Exception as e:
                    errors.append("send_failed:" + repr(e))

        except Exception as e:
            errors.append(repr(e))

    return {"sent": sent, "error": "; ".join(errors)}
