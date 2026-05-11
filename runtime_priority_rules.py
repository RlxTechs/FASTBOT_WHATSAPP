from typing import Optional, Dict, Any
from bot_core import normalize, get_state
from delivery_router import detect_zone, is_location_only, delivery_fee_text, location_received_reply

def no_reply(intent, reason):
    return {
        "reply": "",
        "confidence": 0.0,
        "intent": intent,
        "safe_to_auto_send": False,
        "_no_media": True,
        "debug": {"source": "runtime_priority_rules", "reason": reason}
    }

def is_ack_only(text: str) -> bool:
    m = normalize(text)
    return m in {
        "ok", "okay", "d accord", "daccord", "d'accord",
        "merci", "merci beaucoup", "merci bien",
        "recu", "reçu", "bien recu", "bien reçu",
        "noté", "note", "parfait", "cool", "ça marche", "ca marche"
    }

def asks_about_deleted_messages(message: str) -> bool:
    m = normalize(message)
    return any(x in m for x in [
        "pourquoi vous supprimez",
        "pourquoi vous supprimer",
        "vous supprimez les messages",
        "vous avez supprime",
        "vous avez supprimé",
        "message supprime",
        "message supprimé"
    ])

def is_pending_message(message: str) -> bool:
    m = normalize(message)
    return (
        "en attente de ce message" in m
        or "verifiez votre telephone" in m
        or "vérifiez votre téléphone" in m
    )

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
        "bacongo", "moungali", "talangai", "talangaï", "liberte", "liberté",
        "poto poto", "frites", "yassa", "jus"
    ]
    return any(x in m for x in food_words)

def deleted_message_apology_reply():
    return (
        "Désolé pour la confusion 🙏\n"
        "Il y a eu une erreur dans un message précédent, donc il a été supprimé pour éviter de vous induire en erreur.\n\n"
        "On reprend simplement : dites-moi le plat voulu + votre quartier + votre numéro, "
        "et je vous confirme le total exact avant validation."
    )

def appointment_reply(message: str):
    return (
        "Pour la nourriture, on fonctionne surtout par livraison 🚚\n"
        "Pas besoin de rendez-vous : envoyez simplement le plat voulu + votre quartier + votre numéro.\n\n"
        "Si vous voulez appeler avant, vous pouvez aussi nous joindre directement."
    )

def delivery_question_reply(message: str):
    zone = detect_zone(message)
    return (
        f"{delivery_fee_text(zone)}\n\n"
        "Vous voulez commander quel plat exactement ?"
    )

def payment_confirmation_reply(message: str):
    st = get_state("default")
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

def arabic_more_info_reply():
    return (
        "Bonjour 👋 Oui bien sûr.\n"
        "Nous livrons uniquement sur Brazzaville. 🚚\n\n"
        "Voici nos plats disponibles :\n"
        "• Alloco / bananes frites — 1.000 F\n"
        "• Alloco poulet — 2.000 F\n"
        "• Chawarma poulet — 2.500 F\n"
        "• Chawarma viande — 3.000 F\n"
        "• Riz thieb poulet — 2.500 F\n"
        "• Riz thieb poisson / viande — 3.000 F\n"
        "• Riz poulet yassa — 2.500 F\n"
        "• Hamburger — 3.000 F / 3.500 F\n\n"
        "Pour commander, envoyez le plat + votre quartier + votre numéro."
    )

def after_manual_quote_ack(message: str):
    return (
        "D’accord, c’est noté 👍\n"
        "Je reste disponible pour confirmer la commande."
    )

def try_priority_reply(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    m = normalize(combined_message)
    latest = normalize(latest_message)
    state = get_state(chat_id)

    if is_pending_message(combined_message):
        return no_reply("no_reply_pending_encryption_message", "WhatsApp pending encrypted message")

    if latest and is_ack_only(latest):
        return no_reply("no_reply_ack_only", "acknowledgement only")

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

    if "هل يمكنني الحصول على مزيد من المعلومات" in combined_message or "مزيد من المعلومات" in combined_message:
        return {
            "reply": arabic_more_info_reply(),
            "confidence": 0.94,
            "intent": "arabic_more_info_food_reply",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "arabic_more_info"}
        }

    if "rendez vous" in m or "rendez-vous" in m or "rdv" in m:
        return {
            "reply": appointment_reply(combined_message),
            "confidence": 0.94,
            "intent": "food_rendezvous_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "rendezvous"}
        }

    if "d accord a 10h" in latest or "d’accord a 10h" in latest or "d’accord à 10h" in latest or "je t appelle" in latest or "je t’appelle" in latest:
        return {
            "reply": after_manual_quote_ack(combined_message),
            "confidence": 0.90,
            "intent": "appointment_acknowledgement",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "appointment_ack"}
        }

    delivery_words = [
        "livraison c est combien",
        "livraison c'est combien",
        "la livraison combien",
        "livraison combien",
        "frais de livraison",
        "livraison c est d abord combien",
        "livraison c'est d'abord combien"
    ]

    if any(x in m for x in delivery_words):
        return {
            "reply": delivery_question_reply(combined_message),
            "confidence": 0.94,
            "intent": "food_delivery_fee_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "delivery_fee"}
        }

    if is_location_only(latest) and is_food_like_context(chat_id, combined_message):
        last_item = state.get("last_product_query", "")
        return {
            "reply": location_received_reply(latest, last_item=last_item),
            "confidence": 0.93,
            "intent": "food_location_only_received",
            "safe_to_auto_send": True,
            "_state_patch": {
                "last_category": "food",
                "last_product_family": "food",
                "last_zone_text": latest
            },
            "_no_media": True,
            "debug": {"source": "runtime_priority_rules", "case": "location_only"}
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
