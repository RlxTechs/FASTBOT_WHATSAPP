import json
from pathlib import Path

p = Path("sales_config.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data.setdefault("business", {})
data["business"]["city"] = "Brazzaville"
data["business"]["closing_time"] = "22h"

data.setdefault("addresses", {})

data["addresses"]["food_location_reply"] = (
    "On fait uniquement par livraison pour les plats. 🚚\n"
    "Pas de retrait boutique pour la nourriture.\n\n"
    "Envoyez votre quartier + votre numéro + adresse précise, et on confirme la livraison."
)

data["addresses"]["tech_location_reply"] = (
    "Pour les téléphones portables et les ordinateurs, nous sommes au Centre-ville, côté BEACH. 📍\n"
    "Adresse : avenue Félix Éboué, en face de l’ambassade de Russie.\n\n"
    "Appelez-nous une fois dans les parages pour qu’on vous oriente rapidement."
)

data["addresses"]["general_store_location_reply"] = (
    "Pour les groupes électrogènes, chauffe-eaux, ventilateurs, climatiseurs, bureaux et autres articles, nous sommes à Moungali. 📍\n"
    "Adresse : avenue de la Paix, après le PSP.\n\n"
    "Appelez-nous une fois dans les parages pour qu’on vous oriente rapidement."
)

data["addresses"]["unknown_location_reply"] = (
    "Vous cherchez quel article exactement ?\n\n"
    "L’adresse dépend du type de produit :\n"
    "• Téléphones / ordinateurs : Centre-ville, BEACH, Félix Éboué, en face de l’ambassade de Russie.\n"
    "• Groupes, électroménager, climatiseurs, bureaux, ventilateurs : Moungali, avenue de la Paix, après le PSP.\n"
    "• Nourriture : uniquement par livraison.\n\n"
    "Dites-moi l’article voulu et je vous oriente directement."
)

data.setdefault("delivery", {})
data["delivery"]["only_city"] = "Brazzaville"
data["delivery"]["no_pointe_noire_reply"] = (
    "Désolé, nous ne faisons pas de livraison sur Pointe-Noire pour le moment. 🙏\n"
    "La livraison se fait uniquement sur Brazzaville."
)

data.setdefault("non_food", {})
data["non_food"]["location_reply"] = data["addresses"]["unknown_location_reply"]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ sales_config.json mis à jour avec adresses par catégorie.")
