import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from bot_core import normalize, get_state

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

SALES_CONFIG_PATH = BASE_DIR / "sales_config.json"

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def cfg():
    return load_json(SALES_CONFIG_PATH, {})

def food_cfg():
    return cfg().get("food", {})

FOOD_PRICES = [
    {
        "id": "frites",
        "label": "Portion de frites",
        "price": "1.000 F",
        "aliases": ["frites", "frite"]
    },
    {
        "id": "alloco",
        "label": "Portion d’alloco / bananes frites",
        "price": "1.000 F",
        "aliases": ["alloco", "banane", "bananes", "bananes frites"]
    },
    {
        "id": "alloco_poulet",
        "label": "Alloco poulet",
        "price": "2.000 F",
        "aliases": ["alloco poulet", "banane poulet", "bananes poulet"]
    },
    {
        "id": "alloco_poisson_viande",
        "label": "Alloco poisson / viande",
        "price": "2.500 F",
        "aliases": ["alloco poisson", "alloco viande", "banane poisson", "banane viande"]
    },
    {
        "id": "chawarma_poulet",
        "label": "Chawarma poulet",
        "price": "2.500 F",
        "aliases": ["chawarma poulet", "shawarma poulet"]
    },
    {
        "id": "chawarma_viande",
        "label": "Chawarma viande",
        "price": "3.000 F",
        "aliases": ["chawarma viande", "shawarma viande"]
    },
    {
        "id": "riz_thieb_poulet",
        "label": "Riz thieb poulet",
        "price": "2.500 F",
        "aliases": ["riz thieb poulet", "riz dieb poulet", "riz tieb poulet", "thieb poulet", "dieb poulet"]
    },
    {
        "id": "riz_thieb_poisson_viande",
        "label": "Riz thieb poisson / viande",
        "price": "3.000 F",
        "aliases": ["riz thieb poisson", "riz thieb viande", "riz dieb poisson", "riz dieb viande", "thieb poisson", "thieb viande"]
    },
    {
        "id": "riz_thieb",
        "label": "Riz thieb",
        "price": "2.500 F / 3.000 F selon option",
        "aliases": ["riz thieb", "riz dieb", "riz tieb", "thieb", "dieb"]
    },
    {
        "id": "yassa",
        "label": "Riz poulet yassa",
        "price": "2.500 F",
        "aliases": ["yassa", "riz yassa", "poulet yassa"]
    },
    {
        "id": "hamburger",
        "label": "Hamburger",
        "price": "3.000 F / 3.500 F selon option",
        "aliases": ["hamburger", "burger"]
    }
]

UNKNOWN_FOOD = [
    "pizza", "piza", "pitsa"
]

NON_FOOD_WORDS = [
    "iphone", "telephone", "téléphone", "ordinateur", "laptop", "pc", "imprimante",
    "cartouche", "tv", "frigo", "refrigerateur", "réfrigérateur", "congelateur",
    "congélateur", "groupe", "stabilisateur", "climatiseur", "split"
]

def is_food_context(chat_id: str) -> bool:
    st = get_state(chat_id)
    return (
        st.get("campaign_category") == "food"
        or st.get("last_category") == "food"
        or st.get("campaign_id") == "menu_food"
    )

def has_non_food_words(message: str) -> bool:
    m = normalize(message)
    return any(w in m for w in NON_FOOD_WORDS)

def has_food_signal(message: str) -> bool:
    m = normalize(message)
    if any(w in m for w in UNKNOWN_FOOD):
        return True
    for item in FOOD_PRICES:
        for a in item["aliases"]:
            if normalize(a) in m:
                return True
    return any(x in m for x in ["nourriture", "restaurant", "menu", "plat", "manger", "livrer le", "livrer la"])

def detect_food_item(message: str) -> Optional[Dict[str, str]]:
    m = normalize(message)

    for item in FOOD_PRICES:
        for a in item["aliases"]:
            if normalize(a) in m:
                return item

    # Si le client écrit “riz dieb 2500”, on considère le riz thieb à 2.500.
    if ("riz" in m or "thieb" in m or "dieb" in m) and ("2500" in m or "2 500" in m or "2.500" in m):
        return {
            "id": "riz_thieb_poulet",
            "label": "Riz thieb",
            "price": "2.500 F",
            "aliases": []
        }

    return None

def asks_delivery_order(message: str) -> bool:
    m = normalize(message)
    checks = [
        "possible de me livrer", "livrer", "livrez", "livraison",
        "je suis a", "je suis à", "je suis au", "adresse", "en face",
        "quartier", "gendarmerie", "domicile"
    ]
    return any(x in m for x in checks)

def asks_price(message: str) -> bool:
    m = normalize(message)
    return any(x in m for x in ["combien", "prix", "c est combien", "cest combien", "faites a combien", "faite a combien"])

def detect_unknown_food(message: str) -> Optional[str]:
    m = normalize(message)
    for w in UNKNOWN_FOOD:
        if w in m:
            return "pizza"
    return None

def zone_text(message: str) -> str:
    m = message.strip()
    # On garde simple : on renvoie la zone telle que le client l’a donnée si elle existe.
    markers = ["je suis", "à ", "a ", "au "]
    if any(x in normalize(m) for x in ["bifouiti", "moungali", "total", "moukoundzi", "poto poto", "mpila"]):
        return m
    return "votre zone"

def food_menu_short() -> str:
    return (
        "Voici les plats confirmés aujourd’hui :\n"
        "• Portion de frites — 1.000 F\n"
        "• Alloco / bananes frites — 1.000 F\n"
        "• Alloco poulet — 2.000 F\n"
        "• Chawarma poulet — 2.500 F\n"
        "• Chawarma viande — 3.000 F\n"
        "• Riz thieb poulet — 2.500 F\n"
        "• Riz thieb poisson / viande — 3.000 F\n"
        "• Riz poulet yassa — 2.500 F\n"
        "• Hamburger — 3.000 F / 3.500 F selon option"
    )

def reply_food_item(item: Dict[str, str], message: str) -> str:
    if asks_delivery_order(message):
        return (
            f"Oui, c’est possible ✅\n"
            f"{item['label']} — {item['price']}.\n\n"
            "Livraison uniquement sur Brazzaville. 🚚\n"
            "Pour votre zone, les frais de livraison sont à confirmer selon la distance.\n\n"
            "Envoyez votre numéro + adresse précise / repère, et on vous confirme le total rapidement."
        )

    if asks_price(message):
        return (
            f"Oui, {item['label']} est disponible ✅\n"
            f"Prix : {item['price']}.\n\n"
            "Vous êtes dans quel quartier pour confirmer la livraison ?"
        )

    return (
        f"Oui, {item['label']} est disponible ✅\n"
        f"Prix : {item['price']}.\n\n"
        "Pour commander, envoyez votre quartier + votre numéro + adresse précise."
    )

def reply_unknown_food(name: str) -> str:
    return (
        f"Pour {name}, je dois confirmer si c’est disponible aujourd’hui. 🙏\n\n"
        f"{food_menu_short()}\n\n"
        "Vous voulez prendre quoi exactement ? Envoyez le plat + votre quartier + numéro."
    )

def try_food_sales_reply(message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    # Si le client parle clairement iPhone/ordinateur/etc., on laisse le moteur produits répondre.
    if has_non_food_words(message):
        return None

    if not is_food_context(chat_id) and not has_food_signal(message):
        return None

    unknown = detect_unknown_food(message)
    if unknown:
        return {
            "reply": reply_unknown_food(unknown),
            "confidence": 0.94,
            "intent": "food_unknown_item_check_availability",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food", "last_product_query": unknown},
            "_media_bundle_ids": [],
            "debug": {"source": "food_sales_engine", "case": "unknown_food"}
        }

    item = detect_food_item(message)
    if item:
        return {
            "reply": reply_food_item(item, message),
            "confidence": 0.96,
            "intent": "food_specific_item_order",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food", "last_product_query": item["label"]},
            "_media_bundle_ids": [item["id"], "food_menu"],
            "debug": {"source": "food_sales_engine", "food_item": item["id"]}
        }

    return None
