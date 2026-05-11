import re
from typing import Dict, Any, Optional
from bot_core import normalize, get_state

FOOD_ITEMS = [
    {"id": "alloco_poulet", "label": "Alloco poulet", "price": 2000, "aliases": ["alloco poulet", "alloco + poulet", "alloco+poulet", "banane poulet", "bananes poulet"]},
    {"id": "riz_thieb_poulet", "label": "Riz thieb poulet", "price": 2500, "aliases": ["riz thieb poulet", "riz thied poulet", "riz thiep poulet", "riz dieb poulet", "riz tieb poulet", "thieb poulet", "dieb poulet"]},
    {"id": "riz_thieb", "label": "Riz thieb", "price": 2500, "aliases": ["riz thieb", "riz thied", "riz thiep", "riz dieb", "riz tieb", "thieb", "dieb"]},
    {"id": "hamburger", "label": "Hamburger", "price": 3000, "aliases": ["hamburger", "burger"]},
    {"id": "chawarma_poulet", "label": "Chawarma poulet", "price": 2500, "aliases": ["chawarma poulet", "shawarma poulet"]},
    {"id": "chawarma_viande", "label": "Chawarma viande", "price": 3000, "aliases": ["chawarma viande", "shawarma viande"]},
    {"id": "alloco", "label": "Alloco / bananes frites", "price": 1000, "aliases": ["alloco", "banane", "bananes", "bananes frites"]},
    {"id": "frites", "label": "Portion de frites", "price": 1000, "aliases": ["frites", "frite"]},
    {"id": "yassa", "label": "Riz poulet yassa", "price": 2500, "aliases": ["yassa", "riz yassa", "poulet yassa"]},
]

DRINKS = [
    {"id": "jus_orange", "label": "Jus d’orange", "price": None, "aliases": ["jus d orange", "jus d'orange", "jus orange", "orange"]}
]

DELIVERY_FEES = [
    (["moungali", "mougali", "moungalie"], 500, "Moungali"),
    (["bacongo"], 1000, "Bacongo"),
    (["moukoundzi", "moukoundzigouaka", "total"], 1000, "Total / Moukoundzi"),
    (["poto poto", "potopoto"], 500, "Poto-Poto"),
    (["centre ville", "centre-ville"], 800, "Centre-ville"),
    (["mpila"], 800, "Mpila"),
    (["plateau"], 1000, "Plateau"),
    (["batignolles"], 1000, "Batignolles"),
    (["mayanga"], None, "Mayanga"),
    (["bifouiti"], None, "Bifouiti"),
    (["morgue"], None, "vers la morgue"),
]

NON_FOOD_WORDS = [
    "iphone", "telephone", "téléphone", "ordinateur", "laptop", "pc",
    "imprimante", "cartouche", "tv", "frigo", "refrigerateur",
    "réfrigérateur", "congelateur", "groupe", "stabilisateur",
    "climatiseur", "split", "drone", "drones"
]

def money(n):
    try:
        return f"{int(n):,}".replace(",", ".") + " F"
    except Exception:
        return str(n)

def is_food_context(chat_id: str) -> bool:
    st = get_state(chat_id)
    return (
        st.get("campaign_id") == "menu_food"
        or st.get("campaign_category") == "food"
        or st.get("last_category") == "food"
        or st.get("last_product_family") == "food"
        or st.get("last_product_family") == "pizza"
    )

def has_non_food_words(text: str) -> bool:
    m = normalize(text)
    return any(w in m for w in NON_FOOD_WORDS)

def detect_item(text: str) -> Optional[Dict[str, Any]]:
    m = normalize(text).replace("+", " + ")

    for item in FOOD_ITEMS:
        for a in item["aliases"]:
            if normalize(a) in m:
                return item

    if ("riz" in m or "thieb" in m or "thied" in m or "thiep" in m or "dieb" in m) and ("2500" in m or "2 500" in m or "2.500" in m):
        return {"id": "riz_thieb_poulet", "label": "Riz thieb poulet", "price": 2500, "aliases": []}

    return None

def detect_drink(text: str) -> Optional[Dict[str, Any]]:
    m = normalize(text)
    for d in DRINKS:
        for a in d["aliases"]:
            if normalize(a) in m:
                return d
    return None

def detect_zone(text: str):
    m = normalize(text)
    for aliases, fee, label in DELIVERY_FEES:
        for a in aliases:
            if normalize(a) in m:
                return {"label": label, "fee": fee}

    if any(x in m for x in ["je suis", "avenue", "quartier", "en face", "gendarmerie", "adresse", "rue"]):
        return {"label": "votre zone", "fee": None}

    return None

def asks_time(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in [
        "dans combien de minutes", "combien de minutes", "combien de temps",
        "ca prend combien", "ça prend combien", "delai", "délai",
        "c est pret quand", "c'est prêt quand"
    ])

def quantity_without_item(text: str) -> bool:
    return bool(re.fullmatch(r"\s*\d+\s*x?\s*", normalize(text)))

def is_order_without_context(text: str) -> bool:
    m = normalize(text)
    return (
        "je peux faire la commande" in m
        or "faire la commande" in m
        or "je vous ecris pour ca" in m
        or "je vous écris pour ça" in m
        or "vous allez faire la livraison" in m
    )

def food_signal(text: str) -> bool:
    m = normalize(text)
    return (
        detect_item(text) is not None
        or detect_drink(text) is not None
        or any(x in m for x in ["menu", "nourriture", "restaurant", "plat", "manger", "livrer le", "livrer la", "commande", "livraison"])
    )

def reply_time(zone):
    if zone and zone.get("label") in {"Moungali", "Poto-Poto", "Bacongo"}:
        return (
            f"Pour {zone['label']}, ça prend généralement environ 25 à 45 minutes après confirmation ✅\n"
            "Ça dépend aussi des commandes en cours et du livreur disponible.\n\n"
            "Je vous confirme dès que la commande est lancée."
        )

    return (
        "Le délai dépend de votre zone et des commandes en cours. ⏰\n"
        "En général, on confirme le délai après validation du plat + adresse précise.\n\n"
        "Envoyez votre numéro et le repère exact, puis on vous confirme rapidement."
    )

def reply_order_without_context(zone):
    if zone:
        return (
            f"Oui, livraison possible vers {zone['label']} si c’est à Brazzaville. 🚚\n"
            "Vous voulez commander quel plat exactement ?\n\n"
            "Envoyez le plat + votre numéro, et je vous confirme le total."
        )

    return (
        "Oui, vous pouvez commander ✅\n"
        "Vous voulez quel plat exactement ?\n\n"
        "Envoyez le plat choisi + votre quartier + votre numéro, et je confirme le total."
    )

def reply_order(item, drink, zone):
    lines = ["D’accord ✅"]
    total = int(item["price"])

    lines.append(f"{item['label']} — {money(item['price'])}")

    if drink:
        lines.append(f"{drink['label']} — prix à confirmer")
        lines.append("Le jus d’orange est à confirmer selon disponibilité aujourd’hui.")

    if zone and zone.get("fee") is not None:
        total += int(zone["fee"])
        lines.append(f"Livraison {zone['label']} — {money(zone['fee'])}")
        lines.append("")
        if not drink:
            lines.append(f"Total : {money(total)}.")
        else:
            lines.append(f"Total provisoire sans le jus : {money(total)}.")
        lines.append("Envoyez votre numéro + repère exact, et on confirme la commande.")
        return "\n".join(lines)

    if zone:
        lines.append("")
        lines.append(f"Pour {zone['label']}, les frais de livraison sont à confirmer selon la distance. 🚚")
        lines.append("Envoyez votre numéro + repère exact, et on vous confirme le total.")
        return "\n".join(lines)

    lines.append("")
    lines.append("Vous êtes dans quel quartier pour confirmer la livraison ?")
    return "\n".join(lines)


def asks_tomorrow_order(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in ["pour demain", "demain", "précommande", "precommande"])

def reply_tomorrow_order(item, zone):
    base = (
        f"D’accord, c’est noté pour demain ✅\n"
        f"{item['label']} — {money(item['price'])}.\n\n"
    )

    if zone and zone.get("fee") is not None:
        total = int(item["price"]) + int(zone["fee"])
        base += (
            f"Livraison {zone['label']} — {money(zone['fee'])}\n"
            f"Total : {money(total)}.\n\n"
        )
    elif zone:
        base += f"Livraison vers {zone['label']} : frais à confirmer selon la distance.\n\n"

    base += (
        "Pour valider la précommande, envoyez votre numéro + l’heure souhaitée + le repère exact."
    )
    return base


def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    if has_non_food_words(latest_message) and not is_food_context(chat_id):
        return None

    if not is_food_context(chat_id) and not food_signal(combined_message):
        return None

    zone = detect_zone(combined_message)
    item = detect_item(combined_message)
    drink = detect_drink(combined_message)

    if is_order_without_context(combined_message) and not item:
        return {
            "reply": reply_order_without_context(zone),
            "confidence": 0.94,
            "intent": "food_order_without_item",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "food_order_guard", "case": "order_without_item"}
        }

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

    if item:
        if asks_tomorrow_order(combined_message):
            return {
                "reply": reply_tomorrow_order(item, zone),
                "confidence": 0.97,
                "intent": "food_preorder_tomorrow",
                "safe_to_auto_send": True,
                "_state_patch": {
                    "last_category": "food",
                    "last_product_family": "food",
                    "last_product_query": item["label"],
                    "last_food_item": item["id"],
                    "last_food_price": item["price"]
                },
                "_no_media": True,
                "debug": {"source": "food_order_guard", "case": "tomorrow_preorder"}
            }

        return {
            "reply": reply_order(item, drink, zone),
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
