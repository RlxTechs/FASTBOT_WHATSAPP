import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bot_core import normalize

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

PRODUCTS_PATH = BASE_DIR / "products.json"

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def products_data() -> Dict[str, Any]:
    return load_json(PRODUCTS_PATH, {"products": [], "categories": []})

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

def collect_product_images(product: Dict[str, Any], max_images: int = 4) -> List[str]:
    images = []

    def add(p):
        p = clean_image_path(p)
        if p and image_exists(p) and str((BASE_DIR / p).resolve()) not in images:
            images.append(str((BASE_DIR / p).resolve()))

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
        "tech": ["ordinateur", "laptop", "pc", "hp", "imprimante", "printer", "cartouche", "encre", "epson"],
        "energie": ["groupe", "electrogene", "électrogène", "kva", "stabilisateur", "courant"],
        "refrigerateur": ["frigo", "refrigerateur", "réfrigérateur"],
        "congelateur": ["congelateur", "congélateur"],
        "split": ["split", "climatiseur", "clim"],
        "Papeterie": ["papeterie", "bristol", "bloc notes", "courrier", "perforateur", "sous chemise"],
        "services": ["pack office", "windows", "mac os", "site web", "application", "cybersecurite", "cybersécurité"]
    }

def detect_category(message: str) -> str:
    m = normalize(message)
    best_cat = ""
    best_score = 0

    for cat, words in category_aliases().items():
        score = 0
        for w in words:
            wn = normalize(w)
            if wn and wn in m:
                score += 1
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat if best_score > 0 else ""

def is_price_question(message: str) -> bool:
    m = normalize(message)
    checks = [
        "combien", "prix", "c est combien", "cest combien", "ca coute",
        "ça coute", "tarif", "les prix", "c combien"
    ]
    return any(x in m for x in checks)

def is_product_question(message: str) -> bool:
    m = normalize(message)
    checks = [
        "vous avez", "avez vous", "dispo", "disponible", "je veux",
        "je cherche", "montrez", "envoyez", "combien", "prix", "c est combien"
    ]
    return any(x in m for x in checks)

def find_products_by_category(category_id: str) -> List[Dict[str, Any]]:
    data = products_data()
    out = []

    for p in data.get("products", []) or []:
        if str(p.get("categoryId", "")).lower() == category_id.lower():
            out.append(p)

    return out

def search_products(message: str, limit: int = 8) -> List[Dict[str, Any]]:
    data = products_data()
    m = normalize(message)
    products = data.get("products", []) or []

    scored = []
    for p in products:
        txt = product_text(p)
        score = 0

        # mots du message
        for token in m.split():
            if len(token) >= 3 and token in txt:
                score += 1

        # boost titre / id / catégorie
        title = normalize(p.get("title", ""))
        pid = normalize(p.get("id", ""))
        cat = normalize(p.get("categoryId", ""))

        if title and title in m:
            score += 8
        if pid and pid in m:
            score += 8
        if cat and cat in m:
            score += 4

        # variantes exactes
        for v in p.get("variants", []) or []:
            vn = normalize(v.get("name", ""))
            if vn and vn in m:
                score += 10

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]

def variant_matches_message(product: Dict[str, Any], message: str) -> List[Dict[str, Any]]:
    m = normalize(message)
    matches = []

    for v in product.get("variants", []) or []:
        vn = normalize(v.get("name", ""))

        if vn and vn in m:
            matches.append(v)
            continue

        # cas : “iPhone 13”, “13 Pro Max”, “32 pouces”, “Core i3”
        tokens = [t for t in vn.split() if len(t) >= 2]
        strong = 0
        for t in tokens:
            if t in m:
                strong += 1
        if strong >= 2:
            matches.append(v)

    return matches

def category_iphone_reply(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    lines = [
        "Oui, les iPhone sont disponibles 📱🔥",
        "",
        "Voici les prix selon modèle :"
    ]

    images = []
    product_ids = []

    # Trier dans l’ordre naturel XR, 11, 12...
    def sort_key(p):
        title = normalize(p.get("title", ""))
        if "xr" in title:
            return 10
        nums = re.findall(r"\d+", title)
        return int(nums[0]) if nums else 999

    for p in sorted(products, key=sort_key):
        product_ids.append(p.get("id", ""))

        if p.get("variants"):
            for v in p.get("variants", []):
                lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
                for img in v.get("images", []) or []:
                    img = clean_image_path(img)
                    if image_exists(img):
                        images.append(str((BASE_DIR / img).resolve()))
        else:
            lines.append(f"• {p.get('title')} — {money(p.get('basePrice'))}")

        for img in collect_product_images(p, max_images=1):
            if img not in images:
                images.append(img)

    lines.append("")
    lines.append("Dites-moi le modèle exact que vous voulez, et je vous confirme la disponibilité + livraison/retrait.")

    return {
        "reply": "\n".join(lines),
        "confidence": 0.96,
        "intent": "product_category_iphones_prices",
        "safe_to_auto_send": True,
        "_media_images": images[:4],
        "_product_ids": product_ids,
        "debug": {"source": "products_json", "category": "iphones"}
    }

def product_reply(product: Dict[str, Any], message: str) -> Dict[str, Any]:
    title = product.get("title", "Article")
    availability = product.get("availability", "Disponible")
    variants = product.get("variants", []) or []
    images = collect_product_images(product, max_images=4)

    matched_variants = variant_matches_message(product, message)

    if matched_variants:
        lines = [f"Oui, {title} est disponible ✅", ""]
        for v in matched_variants:
            lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
            for img in v.get("images", []) or []:
                img = clean_image_path(img)
                if image_exists(img):
                    images.insert(0, str((BASE_DIR / img).resolve()))

        lines.append("")
        lines.append(f"Disponibilité : {availability}.")
        lines.append("Vous souhaitez être livré ou venir récupérer ?")
    elif variants:
        lines = [f"Oui, {title} est disponible avec plusieurs choix ✅", ""]
        for v in variants[:12]:
            lines.append(f"• {v.get('name')} — {money(v.get('price'))}")
        lines.append("")
        lines.append("Dites-moi le modèle exact que vous voulez, et je vous confirme rapidement.")
    else:
        lines = [
            f"Oui, {title} est disponible ✅",
            f"Prix : {money(product.get('basePrice'))}",
            f"Disponibilité : {availability}.",
            "",
            "Vous souhaitez être livré ou venir récupérer ?"
        ]

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
        "debug": {"source": "products_json", "product_id": product.get("id", "")}
    }

def try_product_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    if not is_product_question(message):
        return None

    category = detect_category(message)

    if category:
        products = find_products_by_category(category)

        if category == "iphones" and products:
            return category_iphone_reply(products)

        # Si catégorie claire mais pas modèle précis : liste courte de produits
        matches = search_products(message, limit=5)
        if matches:
            return product_reply(matches[0], message)

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
                "debug": {"source": "products_json", "category": category}
            }

    matches = search_products(message, limit=3)
    if matches:
        return product_reply(matches[0], message)

    return None
