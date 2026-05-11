import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from bot_core import normalize, get_state

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

def money(n):
    try:
        return f"{int(n):,}".replace(",", ".") + " F"
    except Exception:
        return str(n)

FOOD_ITEMS = [
    {"id": "riz_thieb_poulet", "label": "Riz thieb poulet", "price": 2500, "aliases": ["riz thieb poulet", "riz thied poulet", "riz dieb poulet", "riz tieb poulet", "thieb poulet", "dieb poulet"]},
    {"id": "riz_thieb", "label": "Riz thieb", "price": 2500, "aliases": ["riz thieb", "riz thied", "riz dieb", "riz tieb", "thieb", "dieb"]},
    {"id": "hamburger", "label": "Hamburger", "price": 3000, "aliases": ["hamburger", "burger"]},
    {"id": "chawarma_poulet", "label": "Chawarma poulet", "price": 2500, "aliases": ["chawarma poulet", "shawarma poulet"]},
    {"id": "chawarma_viande", "label": "Chawarma viande", "price": 3000, "aliases": ["chawarma viande", "shawarma viande"]},
    {"id": "alloco_poulet", "label": "Alloco poulet", "price": 2000, "aliases": ["alloco poulet", "banane poulet", "bananes poulet"]},
    {"id": "alloco", "label": "Alloco / bananes frites", "price": 1000, "aliases": ["alloco", "banane", "bananes", "bananes frites"]},
    {"id": "frites", "label": "Portion de frites", "price": 1000, "aliases": ["frites", "frite"]},
    {"id": "yassa", "label": "Riz poulet yassa", "price": 2500, "aliases": ["yassa", "riz yassa", "poulet yassa"]},
]

UNKNOWN_FOOD = {
    "pizza": ["pizza", "piza", "pitsa"],
    "poulet mayo": ["poulet mayo", "poulet mayonnaise", "poulet mayonaise"]
}

DELIVERY_FEES = [
    (["moungali", "mougali", "moungalie"], 500, "Moungali"),
    (["moukoundzi", "moukoundzigouaka", "total"], 1000, "Total / Moukoundzi"),
    (["poto poto", "potopoto"], 500, "Poto-Poto"),
    (["centre ville", "centre-ville"], 800, "Centre-ville"),
    (["mpila"], 800, "Mpila"),
    (["plateau"], 1000, "Plateau"),
    (["batignolles"], 1000, "Batignolles"),
    (["mayanga"], None, "Mayanga"),
    (["bifouiti"], None, "Bifouiti"),
]

NON_FOOD_WORDS = [
    "iphone", "telephone", "téléphone", "ordinateur", "laptop", "pc",
    "imprimante", "cartouche", "tv", "frigo", "refrigerateur",
    "réfrigérateur", "congelateur", "groupe", "stabilisateur",
    "climatiseur", "split", "drone", "drones"
]

def is_food_context(chat_id: str) -> bool:
    st = get_state(chat_id)
    return (
        st.get("campaign_id") == "menu_food"
        or st.get("campaign_category") == "food"
        or st.get("last_category") == "food"
        or st.get("last_product_family") == "food"
    )

def has_non_food_words(text: str) -> bool:
    m = normalize(text)
    return any(w in m for w in NON_FOOD_WORDS)

def detect_item(text: str) -> Optional[Dict[str, Any]]:
    m = normalize(text)
    for item in FOOD_ITEMS:
        for a in item["aliases"]:
            if normalize(a) in m:
                return item

    if ("riz" in m or "thieb" in m or "thied" in m or "dieb" in m) and ("2500" in m or "2 500" in m or "2.500" in m):
        return {"id": "riz_thieb_poulet", "label": "Riz thieb poulet", "price": 2500, "aliases": []}

    return None

def detect_unknown_food(text: str) -> Optional[str]:
    m = normalize(text)
    for label, aliases in UNKNOWN_FOOD.items():
        for a in aliases:
            if normalize(a) in m:
                return label
    return None

def detect_zone(text: str):
    m = normalize(text)
    for aliases, fee, label in DELIVERY_FEES:
        for a in aliases:
            if normalize(a) in m:
                return {"label": label, "fee": fee}
    if any(x in m for x in ["je suis", "avenue", "quartier", "en face", "gendarmerie", "adresse"]):
        return {"label": "votre zone", "fee": None}
    return None

def asks_time(text: str) -> bool:
    m = normalize(text)
    checks = [
        "dans combien de minutes", "combien de minutes", "ca prend combien",
        "ça prend combien", "combien de temps", "c est pret quand",
        "c'est prêt quand", "delai", "délai"
    ]
    return any(x in m for x in checks)

def quantity_without_item(text: str) -> bool:
    m = normalize(text)
    return bool(re.fullmatch(r"\d+\s*x?", m.strip()))

def food_signal(text: str) -> bool:
    m = normalize(text)
    if detect_item(text) or detect_unknown_food(text):
        return True
    return any(x in m for x in ["menu", "nourriture", "restaurant", "plat", "livrer le", "livrer la", "manger"])

def reply_time(zone):
    if zone and zone.get("label") == "Moungali":
        return (
            "Pour Moungali, ça peut généralement prendre environ 25 à 45 minutes après confirmation ✅\n"
            "Ça dépend aussi du nombre de commandes en cours et du livreur disponible.\n\n"
            "Je vous confirme dès que la commande est lancée."
        )

    return (
        "Le délai dépend de votre zone et des commandes en cours. ⏰\n"
        "En général, on confirme le délai après validation du plat + adresse précise.\n\n"
        "Envoyez votre numéro et le repère exact, puis on vous confirme rapidement."
    )

def reply_unknown_food(name):
    return (
        f"Pour {name}, je dois confirmer si c’est disponible aujourd’hui. 🙏\n\n"
        "Nos plats confirmés actuellement :\n"
        "• Riz thieb poulet — 2.500 F\n"
        "• Riz thieb poisson / viande — 3.000 F\n"
        "• Chawarma poulet — 2.500 F\n"
        "• Chawarma viande — 3.000 F\n"
        "• Alloco poulet — 2.000 F\n"
        "• Hamburger — 3.000 F / 3.500 F selon option\n\n"
        "Vous voulez prendre quoi exactement ?"
    )

def reply_order(item, zone):
    if zone and zone.get("fee") is not None:
        total = int(item["price"]) + int(zone["fee"])
        return (
            f"D’accord ✅\n"
            f"{item['label']} — {money(item['price'])}\n"
            f"Livraison {zone['label']} — {money(zone['fee'])}\n\n"
            f"Total : {money(total)}.\n\n"
            "Envoyez votre numéro + repère exact, et on confirme la commande."
        )

    if zone:
        return (
            f"D’accord ✅\n"
            f"{item['label']} — {money(item['price'])}.\n\n"
            f"Pour {zone['label']}, les frais de livraison sont à confirmer selon la distance. 🚚\n"
            "Envoyez votre numéro + repère exact, et on vous confirme le total."
        )

    return (
        f"Oui, {item['label']} est disponible ✅\n"
        f"Prix : {money(item['price'])}.\n\n"
        "Vous êtes dans quel quartier pour confirmer la livraison ?"
    )

def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    if has_non_food_words(latest_message) and not is_food_context(chat_id):
        return None

    if not is_food_context(chat_id) and not food_signal(combined_message):
        return None

    if quantity_without_item(latest_message):
        return {
            "reply": "D’accord 👍 1 x de quel plat exactement ?",
            "confidence": 0.94,
            "intent": "food_quantity_needs_item",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "food_order_guard", "case": "quantity_without_item"}
        }

    zone = detect_zone(combined_message)
    item = detect_item(combined_message)

    if asks_time(latest_message) or asks_time(combined_message):
        return {
            "reply": reply_time(zone),
            "confidence": 0.95,
            "intent": "food_delivery_time_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "food_order_guard", "case": "time_question"}
        }

    unknown = detect_unknown_food(combined_message)
    if unknown and not item:
        return {
            "reply": reply_unknown_food(unknown),
            "confidence": 0.94,
            "intent": "food_unknown_item_check_availability",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food", "last_product_query": unknown},
            "_media_bundle_ids": [],
            "debug": {"source": "food_order_guard", "case": "unknown_food"}
        }

    if item:
        return {
            "reply": reply_order(item, zone),
            "confidence": 0.96,
            "intent": "food_specific_order_total",
            "safe_to_auto_send": True,
            "_state_patch": {
                "last_category": "food",
                "last_product_family": "food",
                "last_product_query": item["label"],
                "last_food_item": item["id"],
                "last_food_price": item["price"]
            },
            "_media_bundle_ids": [item["id"]],
            "debug": {"source": "food_order_guard", "case": "item_order", "zone": zone}
        }

    if zone and is_food_context(chat_id):
        return {
            "reply": (
                f"D’accord, vous êtes à {zone['label']} 📍\n"
                "Vous souhaitez commander quel plat exactement ?"
            ),
            "confidence": 0.92,
            "intent": "food_location_received_need_item",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food", "last_zone": zone["label"]},
            "_no_media": True,
            "debug": {"source": "food_order_guard", "case": "zone_only"}
        }

    return None
