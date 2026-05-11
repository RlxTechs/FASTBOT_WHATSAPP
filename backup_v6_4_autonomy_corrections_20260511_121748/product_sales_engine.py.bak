import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bot_core import normalize, get_state

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

PRODUCTS_PATH = BASE_DIR / "products.json"
CUSTOM_RULES_PATH = BASE_DIR / "custom_price_rules.json"

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def products_data() -> Dict[str, Any]:
    return load_json(PRODUCTS_PATH, {"products": [], "categories": []})

def custom_rules() -> Dict[str, Any]:
    return load_json(CUSTOM_RULES_PATH, {"items": []})

def money(value: Any) -> str:
    try:
        n = int(value or 0)
    except Exception:
        n = 0
    if n <= 0:
        return "prix selon modèle"
    return f"{n:,}".replace(",", ".") + " F"

def clean_image_path(path: str) -> str:
    path = str(path or "").strip()
    if not path:
        return ""
    if path.startswith("./"):
        path = path[2:]
    return path.replace("\\", "/")

def image_exists(path: str) -> bool:
    if not path:
        return False
    p = BASE_DIR / clean_image_path(path)
    return p.exists() and p.is_file()

def abs_img(path: str) -> str:
    return str((BASE_DIR / clean_image_path(path)).resolve())

def collect_product_images(product: Dict[str, Any], max_images: int = 4) -> List[str]:
    images = []

    def add(p):
        p = clean_image_path(p)
        if p and image_exists(p):
            a = abs_img(p)
            if a not in images:
                images.append(a)

    add(product.get("defaultImage"))

    for img in product.get("gallery", []) or []:
        add(img)

    for v in product.get("variants", []) or []:
        for img in v.get("images", []) or []:
            add(img)
        add(v.get("image"))

    return images[:max_images]

def product_text(product: Dict[str, Any]) -> str:
    chunks = [
        product.get("id", ""),
        product.get("title", ""),
        product.get("subtitle", ""),
        product.get("tag", ""),
        product.get("categoryId", ""),
        product.get("description", "")
    ]
    for v in product.get("variants", []) or []:
        chunks.append(v.get("name", ""))
    return normalize(" ".join(str(x) for x in chunks))

def category_aliases() -> Dict[str, List[str]]:
    return {
        "iphones": ["iphone", "iphones", "apple", "ios", "pro max", "telephone", "téléphone", "smartphone"],
        "tv": ["tv", "television", "télévision", "smart tv", "samsung", "lg", "hisense", "tcl", "east point"],
        "tech": ["ordinateur", "laptop", "pc", "hp", "imprimante", "printer", "cartouche", "encre", "epson", "core i3", "core i5", "core i7"],
        "energie": ["groupe", "electrogene", "électrogène", "kva", "stabilisateur", "courant"],
        "refrigerateur": ["frigo", "refrigerateur", "réfrigérateur"],
        "congelateur": ["congelateur", "congélateur"],
        "split": ["split", "climatiseur", "clim"],
        "Papeterie": ["papeterie", "bristol", "bloc notes", "courrier", "perforateur", "sous chemise"],
        "services": ["pack office", "windows", "mac os", "site web", "application", "cybersecurite", "cybersécurité"]
    }

def detect_category(message: str, state: Dict[str, Any]) -> str:
    m = normalize(message)
    state_cat = normalize(str(state.get("last_category") or state.get("campaign_category") or ""))

    best_cat = ""
    best_score = 0

    for cat, words in category_aliases().items():
        score = 0
        if normalize(cat) == state_cat:
            score += 1
        for w in words:
            wn = normalize(w)
            if wn and wn in m:
                score += 2
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat if best_score > 0 else ""

def is_price_question(message: str) -> bool:
    m = normalize(message)
    checks = [
        "combien", "prix", "pris", "c est combien", "cest combien",
        "ca coute", "ça coute", "tarif", "les prix", "c combien"
    ]
    return any(x in m for x in checks)

def is_product_question(message: str, state: Dict[str, Any]) -> bool:
    m = normalize(message)

    if detect_iphone_model(message, state):
        return True

    checks = [
        "vous avez", "avez vous", "dispo", "disponible", "je veux",
        "je cherche", "montrez", "envoyez", "combien", "prix", "pris",
        "c est combien", "cest combien", "iphone", "imprimante", "laptop",
        "ordinateur", "tv", "groupe", "frigo", "congelateur", "climatiseur"
    ]
    return any(x in m for x in checks)

def find_products_by_category(category_id: str) -> List[Dict[str, Any]]:
    data = products_data()
    return [
        p for p in data.get("products", []) or []
        if str(p.get("categoryId", "")).lower() == category_id.lower()
    ]

def search_products(message: str, limit: int = 8) -> List[Dict[str, Any]]:
    data = products_data()
    m = normalize(message)
    products = data.get("products", []) or []

    scored = []
    for p in products:
        txt = product_text(p)
        score = 0

        for token in m.split():
            if len(token) >= 3 and token in txt:
                score += 1

        title = normalize(p.get("title", ""))
        pid = normalize(p.get("id", ""))
        cat = normalize(p.get("categoryId", ""))

        if title and title in m:
            score += 8
        if pid and pid in m:
            score += 8
        if cat and cat in m:
            score += 4

        for v in p.get("variants", []) or []:
            vn = normalize(v.get("name", ""))
            if vn and vn in m:
                score += 10

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]

def is_iphone_context(state: Dict[str, Any]) -> bool:
    txt = normalize(" ".join([
        str(state.get("last_category", "")),
        str(state.get("campaign_category", "")),
        str(state.get("last_product_family", "")),
        str(state.get("last_product_query", "")),
        str(state.get("campaign_label", ""))
    ]))
    return "iphone" in txt or "iphones" in txt

def detect_iphone_model(message: str, state: Dict[str, Any]) -> str:
    m = normalize(message)

    # XR est court, donc il faut le traiter à part.
    if re.search(r"\bxr\b", m) or "iphone xr" in m:
        return "iPhone XR"

    # iPhone 12 Pro Max, 12 pro max, mes 12 pro max, etc.
    match = re.search(r"\b(7|8|11|12|13|14|15|16|17)\s*(pro max|promax|pro|max|plus|r)?\b", m)
    if match:
        num = match.group(1)
        suffix = (match.group(2) or "").strip()

        if num in {"7", "8"}:
            if "plus" in suffix or "+" in m:
                return f"iPhone {num} Plus"
            return f"iPhone {num}"

        if suffix in {"pro max", "promax"}:
            return f"iPhone {num} Pro Max"
        if suffix == "pro":
            return f"iPhone {num} Pro"
        if suffix == "max":
            return f"iPhone {num} Pro Max"
        if suffix == "plus":
            return f"iPhone {num} Plus"
        if suffix == "r":
            return f"iPhone {num}R"
        return f"iPhone {num}"

    # Si on est déjà dans le sujet iPhone, “pro max” seul ne suffit pas.
    return ""

def custom_rule_reply(label: str, message: str) -> Optional[Dict[str, Any]]:
    label_norm = normalize(label)
    for item in custom_rules().get("items", []) or []:
        aliases = item.get("aliases", []) or []
        all_names = aliases + [item.get("label", ""), item.get("id", "")]
        for a in all_names:
            if normalize(a) == label_norm or normalize(a) in normalize(message):
                images = []
                for img in item.get("images", []) or []:
                    if image_exists(img):
                        images.append(abs_img(img))
                reply = (
                    f"{item.get('label')} — {money(item.get('price'))} ✅\n"
                    f"Disponibilité : {item.get('availability', 'à confirmer')}.\n"
                )
                note = item.get("reply_note", "").strip()
                if note:
                    reply += f"{note}\n"
                reply += "\nVous souhaitez le réserver, être livré ou venir voir sur place ?"
                return {
                    "reply": reply,
                    "confidence": 0.93,
                    "intent": "custom_price_rule",
                    "safe_to_auto_send": True,
                    "_media_images": images,
                    "_state_patch": {
                        "last_category": item.get("categoryId", ""),
                        "last_product_family": item.get("categoryId", ""),
                        "last_product_query": item.get("label", "")
                    },
                    "debug": {"source": "custom_price_rules", "id": item.get("id")}
                }
    return None

def find_iphone_variant(label: str) -> Optional[Dict[str, Any]]:
    target = normalize(label)
    for p in find_products_by_category("iphones"):
        if normalize(p.get("title", "")) == target or target in normalize(p.get("title", "")):
            return {"product": p, "variant": None}

        for v in p.get("variants", []) or []:
            if normalize(v.get("name", "")) == target:
                return {"product": p, "variant": v}

    return None

def iphone_exact_reply(label: str, message: str) -> Optional[Dict[str, Any]]:
    custom = custom_rule_reply(label, message)
    if custom:
        return custom

    found = find_iphone_variant(label)
    if not found:
        available = category_iphone_reply(find_products_by_category("iphones"))
        available["reply"] = (
            f"Pour {label}, je dois confirmer la disponibilité exacte.\n\n"
            "Voici déjà les modèles iPhone actuellement dans notre liste :\n\n"
            + available["reply"].replace("Oui, les iPhone sont disponibles 📱🔥\n\n", "")
        )
        available["intent"] = "iphone_model_not_found_offer_available"
        available["confidence"] = 0.86
        return available

    p = found["product"]
    v = found["variant"]

    images = collect_product_images(p, max_images=3)
    if v:
        for img in v.get("images", []) or []:
            if image_exists(img):
                images.insert(0, abs_img(img))

        reply = (
            f"Oui, {v.get('name')} est disponible 📱✅\n"
            f"Prix : {money(v.get('price'))}\n"
            f"Disponibilité : {p.get('availability', 'Disponible')}.\n\n"
            "Vous souhaitez être livré ou venir récupérer au Centre-ville / BEACH ?"
        )
        state_label = v.get("name", "")
    else:
        reply = (
            f"Oui, {p.get('title')} est disponible 📱✅\n"
            f"Prix : {money(p.get('basePrice'))}\n"
            f"Disponibilité : {p.get('availability', 'Disponible')}.\n\n"
            "Vous souhaitez être livré ou venir récupérer au Centre-ville / BEACH ?"
        )
        state_label = p.get("title", "")

    clean_imgs = []
    for img in images:
        if img not in clean_imgs:
            clean_imgs.append(img)

    return {
        "reply": reply,
        "confidence": 0.96,
        "intent": "iphone_exact_price",
        "safe_to_auto_send": True,
        "_media_images": clean_imgs[:4],
        "_product_ids": [p.get("id", "")],
        "_state_patch": {
            "last_category": "iphones",
            "last_product_family": "iphones",
            "last_product_query": state_label
        },
        "debug": {"source": "products_json", "iphone_model": label}
    }

def category_iphone_reply(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = [
        "Oui, les iPhone sont disponibles 📱🔥",
        "",
        "Voici les prix selon modèle :"
    ]

    images = []
    product_ids = []

    def sort_key(p):
        title = normalize(p.get("title", ""))
        if "xr" in title:
            return 10
        nums = re.findall(r"\d+", title)
        return int(nums[0]) if nums else 999

    count = 0
    for p in sorted(products, key=sort_key):
        product_ids.append(p.get("id", ""))

        if p.get("variants"):
            for v in p.get("variants", []):
                # Pour ne pas envoyer un pavé trop long, on limite un peu.
                if count >= 22:
                    break
                lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
                count += 1
                for img in v.get("images", []) or []:
                    if image_exists(img):
                        images.append(abs_img(img))
        else:
            lines.append(f"• {p.get('title')} — {money(p.get('basePrice'))}")
            count += 1

        for img in collect_product_images(p, max_images=1):
            if img not in images:
                images.append(img)

        if count >= 22:
            break

    lines.append("")
    lines.append("Dites-moi le modèle exact que vous voulez, et je vous confirme la disponibilité + livraison/retrait.")

    clean_imgs = []
    for img in images:
        if img not in clean_imgs:
            clean_imgs.append(img)

    return {
        "reply": "\n".join(lines),
        "confidence": 0.96,
        "intent": "product_category_iphones_prices",
        "safe_to_auto_send": True,
        "_media_images": clean_imgs[:4],
        "_product_ids": product_ids,
        "_state_patch": {
            "last_category": "iphones",
            "last_product_family": "iphones",
            "last_product_query": "iPhones"
        },
        "debug": {"source": "products_json", "category": "iphones"}
    }

def product_reply(product: Dict[str, Any], message: str) -> Dict[str, Any]:
    title = product.get("title", "Article")
    availability = product.get("availability", "Disponible")
    variants = product.get("variants", []) or []
    images = collect_product_images(product, max_images=4)

    matched_variants = []
    m = normalize(message)

    for v in variants:
        vn = normalize(v.get("name", ""))
        if vn and vn in m:
            matched_variants.append(v)
            continue

        tokens = [t for t in vn.split() if len(t) >= 2]
        strong = sum(1 for t in tokens if t in m)
        if strong >= 2:
            matched_variants.append(v)

    if matched_variants:
        lines = [f"Oui, {title} est disponible ✅", ""]
        for v in matched_variants:
            lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
            for img in v.get("images", []) or []:
                if image_exists(img):
                    images.insert(0, abs_img(img))

        lines.append("")
        lines.append(f"Disponibilité : {availability}.")
        lines.append("Vous souhaitez être livré ou venir récupérer ?")
        last_query = matched_variants[0].get("name", title)
    elif variants:
        lines = [f"Oui, {title} est disponible avec plusieurs choix ✅", ""]
        for v in variants[:12]:
            lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
        lines.append("")
        lines.append("Dites-moi le modèle exact que vous voulez, et je vous confirme rapidement.")
        last_query = title
    else:
        lines = [
            f"Oui, {title} est disponible ✅",
            f"Prix : {money(product.get('basePrice'))}",
            f"Disponibilité : {availability}.",
            "",
            "Vous souhaitez être livré ou venir récupérer ?"
        ]
        last_query = title

    clean_imgs = []
    for img in images:
        if img not in clean_imgs:
            clean_imgs.append(img)

    return {
        "reply": "\n".join(lines),
        "confidence": 0.94,
        "intent": "product_from_products_json",
        "safe_to_auto_send": True,
        "_media_images": clean_imgs[:4],
        "_product_ids": [product.get("id", "")],
        "_state_patch": {
            "last_category": product.get("categoryId", ""),
            "last_product_family": product.get("categoryId", ""),
            "last_product_query": last_query
        },
        "debug": {"source": "products_json", "product_id": product.get("id", "")}
    }

def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    state = get_state(chat_id)
    m = normalize(message)

    # Question sur avance / paiement dans un contexte iPhone ou produit.
    if any(x in m for x in ["avance", "avence", "payer petit", "payer une partie", "reservation", "réservation"]):
        return {
            "reply": (
                "Oui, une avance peut être possible pour réserver, mais seulement après confirmation du modèle et de la disponibilité ✅\n\n"
                "Dites-moi le modèle exact + votre quartier, et je vous confirme comment procéder proprement."
            ),
            "confidence": 0.94,
            "intent": "payment_advance_question",
            "safe_to_auto_send": True,
            "_state_patch": {
                "last_category": state.get("last_category", ""),
                "last_product_family": state.get("last_product_family", ""),
                "last_product_query": state.get("last_product_query", "")
            },
            "debug": {"source": "payment_rules"}
        }

    # “Mes le pris”, “le prix”, etc. après un modèle déjà cité.
    if any(x in m for x in ["le prix", "le pris", "mes le prix", "mes le pris", "mais le prix", "mais le pris"]):
        last = state.get("last_product_query", "")
        if last:
            exact = iphone_exact_reply(last, message)
            if exact:
                return exact

    iphone_model = detect_iphone_model(message, state)
    if iphone_model:
        return iphone_exact_reply(iphone_model, message)

    if not is_product_question(message, state):
        return None

    category = detect_category(message, state)

    if category == "iphones":
        return category_iphone_reply(find_products_by_category("iphones"))

    if category:
        matches = search_products(message, limit=5)
        if matches:
            return product_reply(matches[0], message)

        products = find_products_by_category(category)
        if products:
            lines = ["Oui, nous avons ces options disponibles 👇", ""]
            images = []
            product_ids = []

            for p in products[:8]:
                product_ids.append(p.get("id", ""))
                if p.get("variants"):
                    first = p["variants"][0]
                    lines.append(f"• {p.get('title')} — à partir de {money(first.get('price'))}")
                else:
                    lines.append(f"• {p.get('title')} — {money(p.get('basePrice'))}")

                for img in collect_product_images(p, max_images=1):
                    if img not in images:
                        images.append(img)

            lines.append("")
            lines.append("Dites-moi le modèle exact, et je vous confirme le prix + disponibilité.")

            return {
                "reply": "\n".join(lines),
                "confidence": 0.90,
                "intent": "product_category_from_products_json",
                "safe_to_auto_send": True,
                "_media_images": images[:4],
                "_product_ids": product_ids,
                "_state_patch": {
                    "last_category": category,
                    "last_product_family": category,
                    "last_product_query": category
                },
                "debug": {"source": "products_json", "category": category}
            }

    matches = search_products(message, limit=3)
    if matches:
        return product_reply(matches[0], message)

    return None
