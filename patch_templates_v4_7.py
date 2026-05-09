import json
from pathlib import Path

p = Path("response_templates.json")
data = json.loads(p.read_text(encoding="utf-8-sig"))

data.setdefault("templates", {})

data["templates"]["location_question"] = (
    "{business_name} est à {city}. 📍\n"
    "Pour éviter un déplacement inutile, dites-moi d’abord l’article voulu afin de confirmer la disponibilité.\n\n"
    "Vous souhaitez être livré ou venir récupérer chez nous ?"
)

data["templates"]["food_location_delivery_only"] = (
    "On fait uniquement par livraison. 🚚\n"
    "Nos plats sont spéciaux 🔥🍗🍟🍲🛒\n\n"
    "Voici le menu disponible :\n"
    "• Portion de frites — 1.000 F\n"
    "• Portion d’alloco / bananes frites — 1.000 F\n"
    "• Alloco poulet — 2.000 F\n"
    "• Alloco poisson / viande — 2.500 F\n"
    "• Chawarma poulet — 2.500 F\n"
    "• Chawarma viande — 3.000 F\n"
    "• Riz thieb poulet — 2.500 F\n"
    "• Riz thieb poisson / viande — 3.000 F\n"
    "• Riz poulet yassa — 2.500 F\n\n"
    "Envoyez votre quartier + numéro pour confirmer la livraison."
)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("response_templates.json corrigé.")
