from typing import Optional, Dict, Any
from bot_core import normalize, get_state

def no_reply(intent, reason):
    return {
        "reply": "",
        "confidence": 0.0,
        "intent": intent,
        "safe_to_auto_send": False,
        "_no_media": True,
        "debug": {"source": "runtime_priority_rules", "reason": reason}
    }

def asks_about_deleted_messages(message: str) -> bool:
    m = normalize(message)
    checks = [
        "pourquoi vous supprimez",
        "pourquoi vous supprimer",
        "vous supprimez les messages",
        "vous avez supprime",
        "vous avez supprimé",
        "message supprime",
        "message supprimé"
    ]
    return any(x in m for x in checks)

def is_pending_message(message: str) -> bool:
    m = normalize(message)
    return "en attente de ce message" in m or "verifiez votre telephone" in m or "vérifiez votre téléphone" in m

def is_food_like_context(chat_id: str, message: str) -> bool:
    st = get_state(chat_id)
    m = normalize(message)

    if st.get("campaign_id") == "menu_food":
        return True
    if st.get("campaign_category") == "food":
        return True
    if st.get("last_category") == "food":
        return True
    if st.get("last_product_family") in {"food", "pizza"}:
        return True

    food_words = [
        "commande", "livraison", "plat", "riz", "thieb", "thiep", "dieb",
        "alloco", "chawarma", "hamburger", "pizza", "poulet", "morgue",
        "bacongo", "moungali", "poto poto"
    ]
    return any(x in m for x in food_words)

def deleted_message_apology_reply():
    return (
        "Désolé pour la confusion 🙏\n"
        "Il y a eu une erreur dans un message précédent, donc il a été supprimé pour éviter de vous induire en erreur.\n\n"
        "On reprend simplement : dites-moi le plat voulu + votre quartier + votre numéro, "
        "et je vous confirme le total exact avant validation."
    )

def payment_confirmation_reply(message: str):
    return (
        "Oui, c’est possible ✅\n"
        "Le paiement peut se faire à la livraison ou via Mobile Money / Airtel Money après confirmation.\n\n"
        "Pour confirmer le total exact, envoyez-moi simplement :\n"
        "1) le plat choisi\n"
        "2) votre quartier / repère\n"
        "3) l’heure souhaitée\n\n"
        "Comme ça je confirme le montant final avant validation."
    )

def order_without_item_reply(message: str):
    return (
        "Oui, vous pouvez faire la commande ✅\n"
        "Vous voulez commander quel plat exactement ?\n\n"
        "Envoyez le plat + votre quartier + votre numéro, et je vous confirme le total rapidement."
    )

def appointment_reply(message: str):
    return (
        "D’accord, c’est noté 👍\n"
        "Vous pouvez m’appeler à 10h, ou m’envoyer directement le plat voulu pour que je prépare la confirmation."
    )

def try_priority_reply(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    m = normalize(combined_message)
    latest = normalize(latest_message)

    if is_pending_message(combined_message):
        return no_reply("no_reply_pending_encryption_message", "WhatsApp pending encrypted message")

    if asks_about_deleted_messages(combined_message):
        return {
            "reply": deleted_message_apology_reply(),
            "confidence": 0.97,
            "intent": "deleted_message_apology",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "deleted_message_complaint"}
        }

    if "d accord a 10h" in latest or "d’accord a 10h" in latest or "d’accord à 10h" in latest or "je t appelle" in latest or "je t’appelle" in latest:
        return {
            "reply": appointment_reply(combined_message),
            "confidence": 0.92,
            "intent": "appointment_acknowledgement",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "appointment"}
        }

    payment_words = ["paiement", "payer", "sur place", "ça fera combien", "ca fera combien", "total", "confirme la commande"]
    if any(x in m for x in payment_words) and is_food_like_context(chat_id, combined_message):
        return {
            "reply": payment_confirmation_reply(combined_message),
            "confidence": 0.93,
            "intent": "food_payment_confirmation",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "food_payment"}
        }

    order_words = ["je peux faire la commande", "faire la commande", "je vous ecris pour ca", "je vous écris pour ça"]
    if any(x in m for x in order_words):
        return {
            "reply": order_without_item_reply(combined_message),
            "confidence": 0.92,
            "intent": "food_order_without_item_priority",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "order_without_item"}
        }

    return None
