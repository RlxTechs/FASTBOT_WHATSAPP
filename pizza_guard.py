from typing import Optional, Dict, Any

from bot_core import normalize
from lead_memory import get_lead, update_lead

def _result(reply, intent, confidence=0.97, safe=True, patch=None):
    return {
        "reply": reply,
        "confidence": confidence,
        "intent": intent,
        "safe_to_auto_send": safe,
        "_state_patch": patch or {
            "last_category": "food",
            "last_product_family": "pizza",
            "last_product_query": "Pizza / Dürum"
        },
        "_media_bundle_ids": ["pizza", "pizza_durum_menu"],
        "debug": {"source": "pizza_guard", "case": intent}
    }

def is_pizza_message(text: str) -> bool:
    m = normalize(text)

    checks = [
        "pizza", "pizzas", "piza", "pitsa", "pitza",
        "durum", "dürum", "margherita", "kebab", "riene", "poulet", "🍕"
    ]

    return any(x in m for x in checks) or "🍕" in str(text or "")

def menu_standard() -> str:
    return (
        "Voici aussi notre menu standard disponible aujourd’hui 🍽️👇\n\n"
        "• Portion de frites — 1.000 F\n"
        "• Alloco / bananes frites — 1.000 F\n"
        "• Alloco poulet — 2.000 F\n"
        "• Alloco poisson / viande — 2.500 F\n"
        "• Chawarma poulet — 2.500 F\n"
        "• Chawarma viande — 3.000 F\n"
        "• Riz thieb poulet — 2.500 F\n"
        "• Riz thieb poisson / viande — 3.000 F\n"
        "• Riz poulet yassa — 2.500 F\n"
        "• Hamburger — 3.000 F / 3.500 F\n"
    )

def menu_pizza() -> str:
    return (
        "Menu Pizza / Dürum 🍕👇\n\n"
        "• Dürum Poulet — 6.000 F\n"
        "• Dürum Margherita — 7.000 F\n"
        "• Dürum Riene — 8.000 F\n"
        "• Dürum Kebab — 9.000 F\n\n"
        "La disponibilité peut dépendre du moment et du livreur. 🚚\n"
        "Pour commander, envoyez le modèle choisi + votre quartier + votre numéro."
    )

def menu_already_sent(chat_id: str) -> bool:
    lead = get_lead(chat_id)
    last = normalize(lead.get("last_outgoing_text", ""))

    return (
        "portion de frites" in last
        or "alloco poulet" in last
        or "voici notre menu" in last
        or "menu disponible" in last
    )

def pizza_already_sent(chat_id: str) -> bool:
    lead = get_lead(chat_id)
    last = normalize(lead.get("last_outgoing_text", ""))

    return (
        "durum poulet" in last
        or "dürum poulet" in last
        or "durum margherita" in last
        or "dürum margherita" in last
        or "menu pizza" in last
        or "pizza / durum" in last
        or "pizza / dürum" in last
    )

def try_pizza_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    text = combined_message or latest_message or ""

    if not is_pizza_message(text):
        return None

    update_lead(chat_id, {
        "stage": "waiting_location",
        "last_item": "Pizza / Dürum",
        "last_product_query": "Pizza / Dürum"
    })

    if pizza_already_sent(chat_id):
        return _result(
            "Oui, pour la Pizza / Dürum, choisissez juste le modèle voulu 🍕\n\n"
            "• Dürum Poulet — 6.000 F\n"
            "• Dürum Margherita — 7.000 F\n"
            "• Dürum Riene — 8.000 F\n"
            "• Dürum Kebab — 9.000 F\n\n"
            "Envoyez le modèle + votre quartier + votre numéro, et je confirme disponibilité + livraison.",
            "pizza_followup_no_repeat",
            confidence=0.95
        )

    if not menu_already_sent(chat_id):
        reply = (
            "Bonsoir 👋 Oui, on a aussi le menu Pizza / Dürum.\n\n"
            + menu_standard()
            + "\n━━━━━━━━━━━━━━━\n"
            + menu_pizza()
        )
        return _result(reply, "pizza_request_standard_plus_pizza_menu")

    reply = (
        "Oui, voici le menu Pizza / Dürum 🍕👇\n\n"
        "• Dürum Poulet — 6.000 F\n"
        "• Dürum Margherita — 7.000 F\n"
        "• Dürum Riene — 8.000 F\n"
        "• Dürum Kebab — 9.000 F\n\n"
        "La disponibilité peut dépendre du moment et du livreur. 🚚\n"
        "Envoyez le modèle choisi + votre quartier + votre numéro, et je confirme rapidement."
    )

    return _result(reply, "pizza_menu_request")
