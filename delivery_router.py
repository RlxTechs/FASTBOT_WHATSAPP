from typing import Optional, Dict, Any
from bot_core import normalize

ZONES = [
    {
        "name": "Moungali",
        "fee": 500,
        "aliases": ["moungali", "mougali", "moungalie"]
    },
    {
        "name": "Poto-Poto",
        "fee": 500,
        "aliases": ["poto poto", "potopoto", "poto-poto"]
    },
    {
        "name": "Bacongo",
        "fee": 1000,
        "aliases": ["bacongo"]
    },
    {
        "name": "Talangaï / arrêt Liberté",
        "fee": 1000,
        "aliases": ["talangai", "talangaï", "talangai arret liberte", "talangaï arrêt liberté", "arret liberte", "arrêt liberté"]
    },
    {
        "name": "CHU / morgue",
        "fee": 500,
        "aliases": ["chu", "morgue", "morgue chu", "morgue de chu", "morgue du chu"]
    },
    {
        "name": "Total / Moukoundzi",
        "fee": 1000,
        "aliases": ["total", "moukoundzi", "moukoundzigouaka"]
    },
    {
        "name": "Centre-ville",
        "fee": 800,
        "aliases": ["centre ville", "centre-ville", "beach"]
    },
    {
        "name": "Mpila",
        "fee": 800,
        "aliases": ["mpila"]
    },
    {
        "name": "Plateau",
        "fee": 1000,
        "aliases": ["plateau"]
    },
    {
        "name": "Batignolles",
        "fee": 1000,
        "aliases": ["batignolles"]
    },
    {
        "name": "Mayanga",
        "fee": None,
        "aliases": ["mayanga"]
    },
    {
        "name": "Bifouiti",
        "fee": None,
        "aliases": ["bifouiti"]
    },
    {
        "name": "Gare chantier / Tour Espérance",
        "fee": None,
        "aliases": ["gare chantier", "tour esperance", "tour espérance", "orca"]
    }
]

AMBIGUOUS = [
    {
        "word": "liberte",
        "reply": (
            "Vous parlez de Liberté vers Talangaï ou de Liberté côté parc ? 📍\n"
            "Précisez juste le repère exact, comme ça je confirme le bon frais de livraison."
        )
    },
    {
        "word": "liberté",
        "reply": (
            "Vous parlez de Liberté vers Talangaï ou de Liberté côté parc ? 📍\n"
            "Précisez juste le repère exact, comme ça je confirme le bon frais de livraison."
        )
    }
]

LOCATION_MARKERS = [
    "je suis", "suis a", "suis à", "je suis au", "je suis à",
    "quartier", "arret", "arrêt", "avenue", "rue", "face", "en face",
    "collé", "colle", "diagonale", "près", "pres", "proche", "vers"
]

def detect_zone(text: str) -> Optional[Dict[str, Any]]:
    m = normalize(text)

    for z in ZONES:
        for a in z["aliases"]:
            if normalize(a) in m:
                return z

    for amb in AMBIGUOUS:
        if normalize(amb["word"]) in m:
            return {
                "name": "Zone à préciser",
                "fee": None,
                "ambiguous": True,
                "reply": amb["reply"]
            }

    if any(x in m for x in LOCATION_MARKERS):
        return {
            "name": "votre zone",
            "fee": None,
            "unknown": True
        }

    return None

def is_location_only(text: str) -> bool:
    m = normalize(text)

    if not m:
        return False

    product_words = [
        "riz", "thieb", "thiep", "dieb", "alloco", "banane", "chawarma",
        "hamburger", "burger", "pizza", "poulet", "frites", "yassa",
        "iphone", "tv", "ordinateur", "laptop", "frigo", "imprimante"
    ]

    if any(w in m for w in product_words):
        return False

    z = detect_zone(text)
    return bool(z)

def delivery_fee_text(zone: Optional[Dict[str, Any]]) -> str:
    if not zone:
        return (
            "La livraison dépend de votre zone 🚚\n"
            "• Moungali / Poto-Poto : à partir de 500 F\n"
            "• Bacongo / Talangaï / zones plus loin : souvent autour de 1.000 F selon distance\n\n"
            "Envoyez votre quartier + repère exact pour confirmer le montant."
        )

    if zone.get("ambiguous"):
        return zone["reply"]

    if zone.get("fee") is None:
        return (
            f"Pour {zone['name']}, les frais de livraison sont à confirmer selon la distance. 🚚\n"
            "Envoyez votre repère exact et le plat voulu, puis je confirme le total."
        )

    return f"Livraison vers {zone['name']} : {zone['fee']} F. 🚚"

def location_received_reply(text: str, last_item: str = "") -> str:
    zone = detect_zone(text)

    if zone and zone.get("ambiguous"):
        return zone["reply"]

    if zone and zone.get("fee") is not None:
        if last_item:
            return (
                f"D’accord, {delivery_fee_text(zone)}\n"
                f"Votre commande concerne bien : {last_item} ?\n\n"
                "Envoyez votre numéro + repère exact pour confirmer."
            )

        return (
            f"D’accord, {delivery_fee_text(zone)}\n"
            "Vous voulez commander quel plat exactement ?"
        )

    if zone:
        if last_item:
            return (
                f"D’accord, vous êtes vers {zone['name']} 📍\n"
                "Les frais de livraison sont à confirmer selon la distance.\n\n"
                f"Votre commande concerne bien : {last_item} ?"
            )

        return (
            f"D’accord, vous êtes vers {zone['name']} 📍\n"
            "Vous voulez commander quel plat exactement ?"
        )

    return (
        "D’accord 📍\n"
        "Vous voulez commander quel plat exactement ?"
    )
