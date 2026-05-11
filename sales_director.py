from typing import Optional, Dict, Any

from bot_core import normalize, get_state
from lead_memory import get_lead, update_lead
from delivery_router import detect_zone, is_location_only, delivery_fee_text, location_received_reply
from food_order_guard import try_food_order_guard
from product_sales_engine import try_product_sales_reply

def no_reply(intent: str, reason: str):
    return {
        "reply": "",
        "confidence": 0,
        "intent": intent,
        "safe_to_auto_send": False,
        "_no_media": True,
        "debug": {"source": "sales_director", "reason": reason}
    }

def is_ack(text: str) -> bool:
    m = normalize(text)
    return m in {
        "ok", "okay", "d accord", "daccord", "d'accord", "d’accord",
        "merci", "merci beaucoup", "merci bien", "recu", "reçu",
        "bien recu", "bien reçu", "noté", "note", "parfait", "cool",
        "ça marche", "ca marche"
    }

def is_yes_confirmation(text: str) -> bool:
    m = normalize(text)
    return m in {"oui", "yes", "ok oui", "oui confirme", "je confirme", "confirme", "c est bon", "cest bon"}

def is_no_confirmation(text: str) -> bool:
    m = normalize(text)
    return m in {"non", "non merci", "pas maintenant", "apres", "après", "plus tard"}

def wants_delivery_fee(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in [
        "livraison c est combien",
        "livraison c'est combien",
        "la livraison combien",
        "frais de livraison",
        "livraison c est d abord combien",
        "livraison c'est d'abord combien",
        "combien la livraison"
    ])

def asks_time(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in [
        "dans combien de temps",
        "combien de temps",
        "dans combien de minutes",
        "combien de minutes",
        "vous pouvez arriver",
        "vous arrivez quand",
        "delai", "délai"
    ])

def asks_rdv(text: str) -> bool:
    m = normalize(text)
    return "rendez vous" in m or "rendez-vous" in m or "rdv" in m

def asks_deleted(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in [
        "pourquoi vous supprimez",
        "vous supprimez",
        "message supprime",
        "message supprimé",
        "vous avez supprime",
        "vous avez supprimé"
    ])

def is_pending_whatsapp(text: str) -> bool:
    m = normalize(text)
    return "en attente de ce message" in m or "verifiez votre telephone" in m or "vérifiez votre téléphone" in m

def is_generic_more_info(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in [
        "puis je en savoir plus",
        "en savoir plus a ce sujet",
        "en savoir plus à ce sujet",
        "more information"
    ]) or "مزيد من المعلومات" in text

def is_food_context(chat_id: str, text: str) -> bool:
    state = get_state(chat_id)
    lead = get_lead(chat_id)
    m = normalize(text)

    if state.get("campaign_id") == "menu_food":
        return True
    if state.get("campaign_category") == "food":
        return True
    if state.get("last_category") == "food":
        return True
    if state.get("last_product_family") in {"food", "pizza"}:
        return True
    if lead.get("stage") in {"menu_sent", "waiting_item", "waiting_location", "waiting_phone", "waiting_confirmation"}:
        return True

    food_words = [
        "riz", "thieb", "thiep", "dieb", "alloco", "banane", "chawarma",
        "hamburger", "burger", "pizza", "poulet", "frites", "yassa",
        "jus", "plat", "nourriture", "livraison", "commande"
    ]
    return any(x in m for x in food_words)

def menu_food_reply():
    return (
        "Bonjour 👋 Voici notre menu disponible aujourd’hui 🍽️\n\n"
        "• Portion de frites — 1.000 F\n"
        "• Alloco / bananes frites — 1.000 F\n"
        "• Alloco poulet — 2.000 F\n"
        "• Alloco poisson / viande — 2.500 F\n"
        "• Chawarma poulet — 2.500 F\n"
        "• Chawarma viande — 3.000 F\n"
        "• Riz thieb poulet — 2.500 F\n"
        "• Riz thieb poisson / viande — 3.000 F\n"
        "• Riz poulet yassa — 2.500 F\n"
        "• Hamburger — 3.000 F / 3.500 F\n\n"
        "Livraison uniquement sur Brazzaville 🚚\n"
        "Envoyez le plat choisi + votre quartier + votre numéro, et je confirme le total."
    )

def deleted_apology():
    return (
        "Désolé pour la confusion 🙏\n"
        "Il y a eu une erreur dans un message précédent, donc il a été supprimé pour éviter de vous induire en erreur.\n\n"
        "On reprend clairement : envoyez le plat voulu + votre quartier + votre numéro, et je confirme le total exact."
    )

def rdv_reply():
    return (
        "Pour les plats, on fonctionne surtout par livraison 🚚\n"
        "Pas besoin de rendez-vous : envoyez simplement le plat voulu + votre quartier + votre numéro.\n\n"
        "Si vous préférez appeler avant, vous pouvez aussi nous joindre directement."
    )

def time_reply(chat_id: str, text: str):
    zone = detect_zone(text) or detect_zone(get_lead(chat_id).get("last_zone", ""))

    if zone and zone.get("fee") == 500:
        return (
            "Pour cette zone, le délai est généralement autour de 20 à 40 minutes après confirmation ✅\n"
            "Ça dépend aussi des commandes en cours et du livreur disponible.\n\n"
            "Gardez votre téléphone près de vous, le livreur peut appeler."
        )

    return (
        "Le délai dépend de votre zone et des commandes en cours ⏰\n"
        "En général, on confirme le délai après validation du plat + adresse précise.\n\n"
        "Envoyez le repère exact et le numéro, puis je confirme."
    )

def delivery_reply(text: str):
    zone = detect_zone(text)
    return (
        f"{delivery_fee_text(zone)}\n\n"
        "Vous voulez commander quel plat exactement ?"
    )

def confirmation_reply(chat_id: str):
    lead = get_lead(chat_id)
    item = lead.get("last_item") or lead.get("last_product_query") or "votre commande"

    update_lead(chat_id, {"stage": "confirmed", "do_not_followup": True})
    return (
        f"Parfait, c’est confirmé ✅\n"
        f"Commande : {item}.\n\n"
        "Gardez votre téléphone près de vous, on vous contacte si besoin."
    )

def change_money_reply():
    return (
        "D’accord, le livreur va prévoir la monnaie si possible 👍\n"
        "Vous avez 10.000 F sur vous, c’est bien noté.\n\n"
        "Gardez votre téléphone disponible pour l’appel du livreur."
    )

def payment_reply():
    return (
        "Oui, le paiement peut se faire à la livraison ou via Mobile Money / Airtel Money après confirmation ✅\n\n"
        "Envoyez le plat + votre quartier + votre numéro, et je confirme le total exact."
    )

def try_sales_director(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    latest = latest_message or combined_message
    m = normalize(combined_message)
    lead = get_lead(chat_id)

    if is_pending_whatsapp(combined_message):
        return no_reply("no_reply_pending_whatsapp", "pending encrypted whatsapp message")

    if is_ack(latest):
        return no_reply("no_reply_ack", "acknowledgement only")

    if asks_deleted(combined_message):
        return {
            "reply": deleted_apology(),
            "confidence": 0.98,
            "intent": "deleted_message_apology",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "deleted_message"}
        }

    if "10.000" in m or "10000" in m or "differen" in m or "différence" in m:
        return {
            "reply": change_money_reply(),
            "confidence": 0.92,
            "intent": "delivery_change_money",
            "safe_to_auto_send": True,
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "change_money"}
        }

    if is_yes_confirmation(latest) and lead.get("stage") in {"waiting_confirmation", "waiting_phone"}:
        return {
            "reply": confirmation_reply(chat_id),
            "confidence": 0.94,
            "intent": "order_confirmed",
            "safe_to_auto_send": True,
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "yes_confirmation"}
        }

    if is_no_confirmation(latest):
        update_lead(chat_id, {"stage": "closed", "do_not_followup": True})
        return {
            "reply": "D’accord, pas de souci 🙏 Je reste disponible si vous changez d’avis.",
            "confidence": 0.90,
            "intent": "order_declined_or_later",
            "safe_to_auto_send": True,
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "no_confirmation"}
        }

    if asks_rdv(combined_message):
        return {
            "reply": rdv_reply(),
            "confidence": 0.95,
            "intent": "food_rendezvous_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "rdv"}
        }

    if asks_time(combined_message):
        return {
            "reply": time_reply(chat_id, combined_message),
            "confidence": 0.94,
            "intent": "delivery_time_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "time"}
        }

    if wants_delivery_fee(combined_message):
        return {
            "reply": delivery_reply(combined_message),
            "confidence": 0.95,
            "intent": "delivery_fee_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "delivery_fee"}
        }

    if is_location_only(latest) and is_food_context(chat_id, combined_message):
        zone = detect_zone(latest)
        if zone:
            update_lead(chat_id, {
                "last_zone": zone.get("name", latest),
                "stage": "waiting_item" if not lead.get("last_item") else "waiting_phone"
            })

        return {
            "reply": location_received_reply(latest, last_item=lead.get("last_item", "")),
            "confidence": 0.94,
            "intent": "location_received",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "location_only"}
        }

    if "paiement" in m or "payer" in m or "sur place" in m:
        return {
            "reply": payment_reply(),
            "confidence": 0.92,
            "intent": "payment_question",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": True,
            "debug": {"source": "sales_director", "case": "payment"}
        }

    if is_food_context(chat_id, combined_message):
        food = try_food_order_guard(combined_message, latest, chat_id)
        if food:
            item = food.get("_state_patch", {}).get("last_product_query", "")
            if item:
                update_lead(chat_id, {"last_item": item})
            return food

    if is_generic_more_info(combined_message) and is_food_context(chat_id, combined_message):
        update_lead(chat_id, {"stage": "menu_sent"})
        return {
            "reply": menu_food_reply(),
            "confidence": 0.96,
            "intent": "food_menu_sent",
            "safe_to_auto_send": True,
            "_state_patch": {"last_category": "food", "last_product_family": "food"},
            "_no_media": False,
            "debug": {"source": "sales_director", "case": "generic_food"}
        }

    product = try_product_sales_reply(combined_message, chat_id)
    if product:
        return product

    return None
