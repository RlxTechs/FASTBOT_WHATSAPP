import json
from pathlib import Path
from typing import Dict, Any

from bot_core import normalize, get_state
from smart_reply import generate_smart_reply

from app_paths import BASE_DIR
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

def is_food_context(state: Dict) -> bool:
    return (
        state.get("campaign_category") == "food"
        or state.get("last_category") == "food"
        or state.get("campaign_id") == "menu_food"
    )

def has_food_words(msg: str) -> bool:
    m = normalize(msg)
    words = [
        "hamburger", "burger", "alloco", "banane", "frites", "chawarma",
        "riz", "thieb", "yassa", "poulet", "poisson", "viande",
        "nourriture", "restaurant", "manger", "menu", "plat"
    ]
    return any(w in m for w in words)

def asks_pointe_noire(msg: str) -> bool:
    m = normalize(msg)
    return "pointe noire" in m or "pointe-noire" in m or "pointenoire" in m

def asks_show_catalog(msg: str) -> bool:
    m = normalize(msg)
    checks = [
        "vous avez quoi", "vous faites quoi", "ce que vous faites",
        "montrez", "montrer", "envoyez moi ca", "envoyez-moi ca",
        "envoyez moi ça", "catalogue", "produits", "articles",
        "qu est ce que vous vendez", "vous vendez quoi", "vous proposez quoi"
    ]
    return any(x in m for x in checks)

def asks_hamburger(msg: str) -> bool:
    m = normalize(msg)
    return "hamburger" in m or "burger" in m

def asks_location(msg: str) -> bool:
    m = normalize(msg)
    checks = [
        "vous etes ou", "ou etes vous", "dans quelle ville", "dans quel ville",
        "pointe noire", "adresse", "localisation", "emplacement",
        "restaurant ou", "boutique ou", "magasin ou", "ville"
    ]
    return any(x in m for x in checks)

def asks_delivery(msg: str) -> bool:
    m = normalize(msg)
    checks = ["livraison", "livrez", "livrer", "domicile", "chez moi", "transport", "frais"]
    return any(x in m for x in checks)

def asks_order(msg: str) -> bool:
    m = normalize(msg)
    checks = ["commander", "commande", "je prends", "je veux prendre", "reserver", "acheter", "livrez moi"]
    return any(x in m for x in checks)

def food_menu(prefix: str = "") -> str:
    c = cfg()
    food = c.get("food", {})
    lines = []

    if prefix.strip():
        lines.append(prefix.strip())
        lines.append("")

    lines.append(food.get("brand_line", "Nos plats sont spéciaux 🔥🍗🍟🍲🛒"))
    lines.append(food.get("delivery_only_line", "On fait uniquement par livraison. 🚚"))
    lines.append("")
    lines.append("Voici le menu disponible :")

    for item in food.get("items", []):
        lines.append(f"• {item.get('name')} — {item.get('price')}")

    lines.append("")
    lines.append(food.get("delivery_note", "Livraison selon votre zone."))
    lines.append("")
    lines.append(food.get("order_cta", "Pour commander, envoyez le plat choisi + votre quartier + votre numéro."))

    return "\n".join(lines).strip()

def catalog_overview() -> str:
    return cfg().get("non_food", {}).get("catalog_overview", "Nous proposons plusieurs produits et services. Dites-moi ce que vous cherchez.")

def pointe_noire_food_reply() -> str:
    return (
        "Pour les plats, on fonctionne uniquement par livraison. 🚚\n"
        "Nous sommes surtout organisés pour les livraisons locales à Brazzaville selon les zones.\n\n"
        + food_menu("Nos plats sont spéciaux 🔥🍗🍟🍲🛒")
    )

def pointe_noire_non_food_reply() -> str:
    return cfg().get("non_food", {}).get(
        "pointe_noire_reply",
        "Nous sommes basés à Brazzaville. Dites-moi l’article voulu pour confirmer la livraison."
    )

def hamburger_reply() -> str:
    return (
        "Oui, hamburger disponible 🍔🔥\n"
        "Prix : 3.000 F / 3.500 F selon option.\n\n"
        "On fait uniquement par livraison. 🚚\n"
        "Envoyez votre quartier + numéro + adresse précise pour confirmer la livraison.\n\n"
        + food_menu("Voici aussi le menu complet :")
    )

def food_combined_reply(message: str) -> str:
    parts = []

    if asks_pointe_noire(message):
        parts.append(
            "Concernant Pointe-Noire : pour les plats, on fonctionne surtout en livraison locale selon zone. "
            "Envoyez votre quartier exact pour confirmer si la livraison est possible."
        )

    if asks_hamburger(message):
        parts.append(
            "Oui, hamburger disponible 🍔🔥\n"
            "Prix : 3.000 F / 3.500 F selon option."
        )

    if asks_location(message):
        parts.append("On fait uniquement par livraison pour les plats, pas de retrait boutique.")

    if asks_delivery(message):
        parts.append("Livraison disponible selon votre zone. Envoyez votre quartier pour confirmer le frais.")

    if asks_show_catalog(message) or has_food_words(message) or asks_order(message):
        parts.append(food_menu("Nos plats sont spéciaux 🔥🍗🍟🍲🛒"))

    if not parts:
        parts.append(food_menu("Bonjour 👋 Vous venez sûrement de la Pub Menu nourriture. 🍽️"))

    # Évite les doublons exacts
    clean = []
    for p in parts:
        if p.strip() and p.strip() not in clean:
            clean.append(p.strip())

    return "\n\n".join(clean)

def global_combined_reply(message: str, chat_id: str) -> Dict:
    state = get_state(chat_id)
    m = normalize(message)

    # 1) Si contexte nourriture OU mots nourriture, priorité restaurant.
    if is_food_context(state) or has_food_words(message):
        return {
            "reply": food_combined_reply(message),
            "confidence": 0.95,
            "intent": "sales_multi_food",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_food"}
        }

    # 2) Pointe-Noire hors nourriture.
    if asks_pointe_noire(message):
        return {
            "reply": pointe_noire_non_food_reply(),
            "confidence": 0.93,
            "intent": "sales_pointe_noire_non_food",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_city"}
        }

    # 3) “Vous avez quoi / montrez ce que vous faites” = catalogue global.
    if asks_show_catalog(message):
        return {
            "reply": catalog_overview(),
            "confidence": 0.94,
            "intent": "sales_catalog_overview",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_catalog"}
        }

    # 4) Sinon, utiliser le cerveau actuel.
    return generate_smart_reply(message, chat_id=chat_id)

def generate_sales_reply(message: str, chat_id: str = "default") -> Dict:
    return global_combined_reply(message, chat_id)
