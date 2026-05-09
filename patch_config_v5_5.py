import json
from pathlib import Path

# sales_config.json
p = Path("sales_config.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data.setdefault("business", {})
data["business"]["city"] = "Brazzaville"
data["business"]["closing_time"] = "22h"

data.setdefault("delivery", {})
data["delivery"]["only_city"] = "Brazzaville"
data["delivery"]["no_delivery_cities"] = ["Pointe-Noire", "Pointe Noire", "Point-Noire"]
data["delivery"]["no_pointe_noire_reply"] = (
    "Désolé, nous ne faisons pas de livraison sur Pointe-Noire pour le moment. 🙏\n"
    "La livraison se fait uniquement sur Brazzaville.\n\n"
    "Si vous êtes à Brazzaville, envoyez votre quartier + votre numéro pour confirmer la livraison."
)

data.setdefault("food", {})
data["food"]["closing_time_reply"] = (
    "On ferme à 22h. ⏰\n"
    "Pour être servi rapidement, commandez avant 22h si possible.\n\n"
    "Envoyez le plat choisi + votre quartier + votre numéro + adresse précise."
)

data["food"]["pointe_noire_reply"] = (
    "Désolé, on ne livre pas sur Pointe-Noire pour le moment. 🙏\n"
    "Nos livraisons sont uniquement sur Brazzaville.\n\n"
    "Si vous êtes à Brazzaville, envoyez votre quartier + votre numéro pour commander."
)

data.setdefault("non_food", {})
data["non_food"]["opening_hours_reply"] = (
    "Nous fermons à 22h. ⏰\n"
    "Pour éviter un déplacement inutile, confirmez d’abord l’article voulu avant de venir.\n\n"
    "Vous souhaitez être livré ou venir récupérer chez nous ?"
)

data["non_food"]["pointe_noire_reply"] = (
    "Désolé, nous ne faisons pas de livraison sur Pointe-Noire pour le moment. 🙏\n"
    "La livraison se fait uniquement sur Brazzaville.\n\n"
    "Dites-moi l’article voulu, et si vous êtes à Brazzaville, envoyez votre quartier pour confirmer la livraison."
)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# response_templates.json
rp = Path("response_templates.json")
if rp.exists():
    rdata = json.loads(rp.read_text(encoding="utf-8-sig"))
else:
    rdata = {"templates": {}}

rdata.setdefault("templates", {})
rdata["templates"]["opening_hours"] = (
    "Nous fermons à 22h. ⏰\n"
    "Pour commander ou vérifier un article, envoyez-moi directement ce que vous voulez + votre quartier."
)

rdata["templates"]["delivery_question"] = (
    "Oui, livraison possible uniquement sur Brazzaville. 🚚\n"
    "Moungali/environs peut commencer à 500 F, zones plus loin à partir de 800 F selon distance.\n\n"
    "Envoyez votre quartier + adresse précise pour confirmer le montant exact."
)

rp.write_text(json.dumps(rdata, ensure_ascii=False, indent=2), encoding="utf-8")

print("✅ Config mise à jour : fermeture 22h + livraison Brazzaville uniquement.")
