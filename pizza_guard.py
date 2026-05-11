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
        "durum", "dürum", "margherita", "kebab", "riene", "🍕"
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
        "• Dürum Margherita — 5.000 F / 5.500 F\n"
        "• Dürum Riene — 6.000 F / 6.500 F\n"
        "• Dürum Kebab — 6.000 F / 6.500 F\n\n"
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
        "durum margherita" in last
        or "dürum margherita" in last
        or "menu pizza" in last
        or "pizza / durum" in last
        or "pizza / dürum" in last
    )

def asks_price(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in ["combien", "prix", "c est a combien", "c'est a combien", "c'est à combien"])

def asks_availability(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in ["disponible", "c est bon", "c'est bon", "vous avez", "possible"])

def try_pizza_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    text = combined_message or latest_message or ""

    if not is_pizza_message(text):
        return None

    update_lead(chat_id, {
        "stage": "waiting_location",
        "last_item": "Pizza / Dürum",
        "last_product_query": "Pizza / Dürum"
    })

    # Si on a déjà envoyé le menu pizza, éviter de répéter.
    if pizza_already_sent(chat_id):
        return _result(
            "Oui, pour la pizza/Dürum, choisissez juste le modèle voulu 🍕\n\n"
            "Envoyez le modèle + votre quartier + votre numéro, et je confirme disponibilité + livraison.",
            "pizza_followup_no_repeat",
            confidence=0.95
        )

    # Si le menu standard n'a pas encore été envoyé, on envoie standard + pizza.
    if not menu_already_sent(chat_id):
        reply = (
            "Bonsoir 👋 Oui, on a aussi le menu Pizza / Dürum.\n\n"
            + menu_standard()
            + "\n━━━━━━━━━━━━━━━\n"
            + menu_pizza()
        )
        return _result(reply, "pizza_request_standard_plus_pizza_menu")

    # Si menu standard déjà envoyé, envoyer seulement pizza.
    reply = (
        "Oui, voici le menu Pizza / Dürum 🍕👇\n\n"
        "• Dürum Margherita — 5.000 F / 5.500 F\n"
        "• Dürum Riene — 6.000 F / 6.500 F\n"
        "• Dürum Kebab — 6.000 F / 6.500 F\n\n"
        "La disponibilité peut dépendre du moment et du livreur. 🚚\n"
        "Envoyez le modèle choisi + votre quartier + votre numéro, et je confirme rapidement."
    )

    return _result(reply, "pizza_menu_request")
