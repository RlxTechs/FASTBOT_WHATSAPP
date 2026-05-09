import json
from pathlib import Path

p = Path("sales_config.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data.setdefault("food", {})
data["food"]["brand_line"] = "Nos plats sont spéciaux 🔥🍗🍟🍲🛒"
data["food"]["delivery_only_line"] = "On fait uniquement par livraison. 🚚"
data["food"]["order_cta"] = "Pour commander, envoyez le plat choisi + votre quartier + votre numéro + adresse précise."
data["food"]["delivery_note"] = "Livraison selon votre zone. Moungali/environs peut commencer à 500 F, zones plus loin à partir de 800 F selon distance."

items = data["food"].setdefault("items", [])
existing = {str(x.get("name","")).lower(): x for x in items}

def upsert(name, price):
    key = name.lower()
    if key in existing:
        existing[key]["price"] = price
    else:
        items.append({"name": name, "price": price})

upsert("Portion de frites", "1.000 F")
upsert("Portion d’alloco / bananes frites", "1.000 F")
upsert("Alloco poulet", "2.000 F")
upsert("Alloco poisson / viande", "2.500 F")
upsert("Chawarma poulet", "2.500 F")
upsert("Chawarma viande", "3.000 F")
upsert("Riz thieb poulet", "2.500 F")
upsert("Riz thieb poisson / viande", "3.000 F")
upsert("Riz poulet yassa", "2.500 F")
upsert("Hamburger", "3.000 F / 3.500 F selon option")

data.setdefault("non_food", {})
data["non_food"]["catalog_overview"] = (
    "Voici ce que nous proposons chez O'CG / BZ STORE 👇\n\n"
    "🍽️ Restauration : alloco, chawarma, riz, yassa, hamburger...\n"
    "📺 TV Smart : East Point, TCL, Hisense, LG, Samsung\n"
    "🧊 Électroménager : frigos, congélateurs, splits/climatiseurs, machines à laver, micro-ondes\n"
    "⚡ Énergie : groupes électrogènes, stabilisateurs, solutions courant\n"
    "💻 Informatique / bureautique : laptops HP, imprimantes, cartouches, encres, Pack Office, Windows\n"
    "📄 Papeterie : sous-chemises, bristol, bloc-notes, courrier, perforateurs...\n"
    "📱 iPhones : plusieurs séries disponibles selon stock\n"
    "🛠️ Services : installation Windows/Mac, sites web, applications, automatisation, cybersécurité\n\n"
    "Dites-moi ce qui vous intéresse exactement, ou envoyez une capture de la pub, et je vous donne le prix + disponibilité."
)

data["non_food"]["pointe_noire_reply"] = (
    "Nous sommes basés à Brazzaville. 📍\n"
    "Pour Pointe-Noire, dites-moi d’abord l’article voulu : je vous confirme si une solution de livraison/expédition est possible.\n\n"
    "Vous cherchez quel produit exactement ?"
)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("sales_config.json optimisé V5.3")
