import json
from pathlib import Path

CAMPAIGNS_PATH = Path("campaigns.json")

defaults = [
    {
        "id": "menu_food",
        "label": "Pub Menu nourriture",
        "category": "food",
        "intent": "food_menu",
        "product_id": "",
        "product_query": "menu nourriture",
        "keywords": ["menu", "nourriture", "alloco", "banane", "chawarma", "riz", "thieb", "yassa", "plat", "restaurant"],
        "hashes": []
    },
    {
        "id": "groupes_electrogenes",
        "label": "Pub Groupes électrogènes",
        "category": "energie",
        "intent": "product",
        "product_id": "groupe-electrogene",
        "product_query": "groupe electrogene",
        "keywords": ["groupe", "electrogene", "électrogène", "kva", "energie", "courant", "diesel", "essence"],
        "hashes": []
    },
    {
        "id": "stabilisateurs",
        "label": "Pub Stabilisateurs",
        "category": "energie",
        "intent": "product_category",
        "product_id": "",
        "product_query": "stabilisateur",
        "keywords": ["stabilisateur", "east point", "1000va", "2000va", "5000va", "tension", "courant"],
        "hashes": []
    },
    {
        "id": "tv_smart",
        "label": "Pub TV Smart",
        "category": "tv",
        "intent": "product_category",
        "product_id": "",
        "product_query": "tv smart",
        "keywords": ["tv", "television", "télévision", "smart", "samsung", "lg", "tcl", "hisense", "east point"],
        "hashes": []
    },
    {
        "id": "electromenager_general",
        "label": "Pub Électroménager",
        "category": "electromenager",
        "intent": "product_category",
        "product_id": "",
        "product_query": "electromenager",
        "keywords": ["electromenager", "électroménager", "frigo", "congelateur", "split", "machine a laver", "micro onde"],
        "hashes": []
    },
    {
        "id": "electromenager_frigo",
        "label": "Pub Réfrigérateurs",
        "category": "refrigerateur",
        "intent": "product_category",
        "product_id": "west-pool-frigo",
        "product_query": "refrigerateur",
        "keywords": ["frigo", "refrigerateur", "réfrigérateur", "litres", "west pool"],
        "hashes": []
    },
    {
        "id": "electromenager_congelateur",
        "label": "Pub Congélateurs",
        "category": "congelateur",
        "intent": "product_category",
        "product_id": "congelo-pic",
        "product_query": "congelateur",
        "keywords": ["congelateur", "congélateur", "congelo", "litres", "west pool"],
        "hashes": []
    },
    {
        "id": "electromenager_split",
        "label": "Pub Climatiseurs / Split",
        "category": "split",
        "intent": "product_category",
        "product_id": "nasco-clim",
        "product_query": "climatiseur split",
        "keywords": ["split", "clim", "climatiseur", "chevaux", "nasco", "west pool"],
        "hashes": []
    },
    {
        "id": "iphone_series",
        "label": "Pub iPhones",
        "category": "iphones",
        "intent": "product_category",
        "product_id": "",
        "product_query": "iphone",
        "keywords": ["iphone", "apple", "pro max", "pro", "plus"],
        "hashes": []
    },
    {
        "id": "laptop_hp",
        "label": "Pub Ordinateur Laptop HP",
        "category": "tech",
        "intent": "product",
        "product_id": "laptop-hp",
        "product_query": "ordinateur laptop hp",
        "keywords": ["ordinateur", "laptop", "pc", "core i3", "core i5", "core i7", "hp"],
        "hashes": []
    }
]

if CAMPAIGNS_PATH.exists():
    data = json.loads(CAMPAIGNS_PATH.read_text(encoding="utf-8-sig"))
else:
    data = {"version": 1, "match_threshold": 10, "campaigns": []}

data.setdefault("version", 1)
data.setdefault("match_threshold", 10)
data.setdefault("campaigns", [])

existing = {c.get("id"): c for c in data["campaigns"]}

for d in defaults:
    if d["id"] not in existing:
        data["campaigns"].append(d)
    else:
        c = existing[d["id"]]
        for k, v in d.items():
            if k == "hashes":
                c.setdefault("hashes", [])
            elif k == "keywords":
                old = c.setdefault("keywords", [])
                for kw in v:
                    if kw not in old:
                        old.append(kw)
            else:
                c.setdefault(k, v)

CAMPAIGNS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("campaigns.json prêt, sans effacer les anciens apprentissages.")
