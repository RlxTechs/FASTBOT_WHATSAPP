from typing import Optional, Dict, Any

from bot_core import normalize
from lead_memory import get_lead, update_lead

def result(reply, intent, confidence=0.94, safe=True, patch=None, no_media=True, debug_case=""):
    return {
        "reply": reply,
        "confidence": confidence,
        "intent": intent,
        "safe_to_auto_send": safe,
        "_state_patch": patch or {"last_category": "food", "last_product_family": "food"},
        "_no_media": no_media,
        "debug": {"source": "smart_overrides", "case": debug_case}
    }

def no_reply(intent, reason):
    return {
        "reply": "",
        "confidence": 0,
        "intent": intent,
        "safe_to_auto_send": False,
        "_no_media": True,
        "debug": {"source": "smart_overrides", "reason": reason}
    }

def is_pending(text):
    m = normalize(text)
    return "en attente de ce message" in m or "verifiez votre telephone" in m or "vérifiez votre téléphone" in m

def is_simple_greeting(text):
    m = normalize(text)
    return m in {"bonjour", "bonsoir", "bjr", "bsr", "salut", "slt", "hello", "cc"}

def menu_already_sent(chat_id):
    lead = get_lead(chat_id)
    last = normalize(lead.get("last_outgoing_text", ""))
    return (
        "voici notre menu" in last
        or "voici le menu disponible" in last
        or "portion de frites" in last
        or "alloco poulet" in last
    )

def asks_tomorrow(text):
    m = normalize(text)
    return any(x in m for x in ["demain", "commande demain", "ferai le commande", "ferai la commande", "pour demain"])

def asks_delivery_process(text):
    m = normalize(text)
    return any(x in m for x in [
        "livraison ça se passe comment",
        "livraison ca se passe comment",
        "la livraison se passe comment",
        "comment se passe la livraison",
        "livraison ça c'est passe comment",
        "livraison ca c'est passe comment"
    ])

def asks_delivery_fee(text):
    m = normalize(text)
    return any(x in m for x in [
        "livrez pour combien",
        "livraison combien",
        "combien la livraison",
        "frais de livraison",
        "livraison c est combien",
        "livraison c'est combien"
    ])

def detect_zone(text):
    m = normalize(text)

    if "ouenze" in m or "ouenzé" in m:
        return ("Ouenzé", "800 F")

    if "kintélé" in m or "kintele" in m:
        return ("Kintélé", "à confirmer avec le livreur selon le repère exact")

    if "moungali" in m or "mougali" in m:
        return ("Moungali", "500 F")

    if "poto" in m:
        return ("Poto-Poto", "500 F")

    if "bacongo" in m:
        return ("Bacongo", "1.000 F")

    if "talangai" in m or "talangaï" in m:
        return ("Talangaï", "1.000 F environ selon le repère")

    if "mayanga" in m:
        return ("Mayanga", "à confirmer selon la distance")

    return ("votre zone", "à confirmer selon la distance")

def try_smart_override(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    combined = combined_message or ""
    latest = latest_message or combined

    if is_pending(combined):
        return no_reply("no_reply_pending_whatsapp", "message WhatsApp pas encore déchiffré")

    if is_simple_greeting(latest) and menu_already_sent(chat_id):
        return result(
            "Bonsoir 👋 Je vous écoute. Vous voulez commander quel plat exactement ?",
            "greeting_after_menu_no_repeat",
            confidence=0.95,
            debug_case="greeting_after_menu"
        )

    if asks_tomorrow(combined):
        update_lead(chat_id, {"stage": "waiting_item", "last_order_timing": "demain"})
        return result(
            "Oui, c’est possible pour demain ✅\n\n"
            "Pour préparer correctement, envoyez simplement :\n"
            "1) le plat voulu\n"
            "2) l’heure souhaitée\n"
            "3) votre quartier / repère\n"
            "4) votre numéro\n\n"
            "Comme ça je confirme le total avec livraison.",
            "food_preorder_tomorrow_clear",
            confidence=0.96,
            debug_case="tomorrow_order"
        )

    if asks_delivery_process(combined):
        return result(
            "La livraison se passe simplement 🚚\n\n"
            "1) Vous choisissez le plat.\n"
            "2) Vous envoyez votre quartier + repère exact + numéro.\n"
            "3) On confirme le total avec les frais de livraison.\n"
            "4) Le livreur vous appelle une fois proche ou arrivé.\n"
            "5) Paiement possible à la livraison ou en avance par Mobile Money / Airtel Money.\n\n"
            "Vous êtes dans quel quartier pour que je confirme les frais ?",
            "delivery_process_explained",
            confidence=0.97,
            debug_case="delivery_process"
        )

    if asks_delivery_fee(combined):
        zone, fee = detect_zone(combined)
        if zone == "votre zone":
            return result(
                "La livraison dépend de votre zone 🚚\n\n"
                "Moungali / Poto-Poto : souvent à partir de 500 F.\n"
                "Ouenzé / Bacongo / Talangaï : souvent autour de 800 F à 1.000 F selon le repère.\n"
                "Kintélé et zones plus loin : à confirmer avec le livreur.\n\n"
                "Vous êtes dans quel quartier exactement ?",
                "delivery_fee_general",
                confidence=0.94,
                debug_case="delivery_fee_general"
            )

        return result(
            f"Pour {zone}, la livraison est {fee}. 🚚\n\n"
            "Vous voulez commander quel plat exactement ?",
            "delivery_fee_by_zone",
            confidence=0.95,
            debug_case="delivery_fee_zone"
        )

    m = normalize(latest)
    zone_keywords = ["ouenze", "ouenzé", "kintélé", "kintele", "moungali", "mougali", "poto", "bacongo", "talangai", "talangaï"]
    if any(z in m for z in zone_keywords):
        zone, fee = detect_zone(latest)
        update_lead(chat_id, {"last_zone": zone})
        return result(
            f"D’accord, vous êtes à {zone} 📍\n"
            f"Livraison : {fee}.\n\n"
            "Vous voulez commander quel plat exactement ?",
            "zone_received_delivery_fee",
            confidence=0.94,
            debug_case="zone_only"
        )

    return None
