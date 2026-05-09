import json
from pathlib import Path

path = Path("campaigns.json")

defaults = [
    {"id":"menu_food","label":"Pub Menu nourriture","category":"food","intent":"food_menu","product_id":"","product_query":"menu nourriture","keywords":["menu","nourriture","restaurant","alloco","chawarma","riz","thieb","yassa"],"hashes":[]},
    {"id":"groupes_electrogenes","label":"Pub Groupes électrogènes","category":"energie","intent":"product","product_id":"groupe-electrogene","product_query":"groupe electrogene","keywords":["groupe","electrogene","kva","energie","courant"],"hashes":[]},
    {"id":"stabilisateurs","label":"Pub Stabilisateurs","category":"energie","intent":"product_category","product_id":"","product_query":"stabilisateur","keywords":["stabilisateur","1000va","2000va","5000va","tension"],"hashes":[]},
    {"id":"tv_smart","label":"Pub TV Smart","category":"tv","intent":"product_category","product_id":"","product_query":"tv smart","keywords":["tv","smart","television","samsung","lg","tcl","hisense"],"hashes":[]},
    {"id":"electromenager_general","label":"Pub Électroménager","category":"electromenager","intent":"product_category","product_id":"","product_query":"electromenager","keywords":["frigo","congelateur","split","climatiseur","machine a laver"],"hashes":[]},
    {"id":"iphone_series","label":"Pub iPhones","category":"iphones","intent":"product_category","product_id":"","product_query":"iphone","keywords":["iphone","apple","pro max"],"hashes":[]},
    {"id":"laptop_hp","label":"Pub Ordinateur Laptop HP","category":"tech","intent":"product","product_id":"laptop-hp","product_query":"ordinateur laptop hp","keywords":["ordinateur","laptop","core i3","core i5","core i7","hp"],"hashes":[]}
]

if path.exists():
    data = json.loads(path.read_text(encoding="utf-8-sig"))
else:
    data = {"version": 1, "match_threshold": 10, "campaigns": []}

data.setdefault("version", 1)
data.setdefault("match_threshold", 10)
data.setdefault("campaigns", [])

by_id = {c.get("id"): c for c in data["campaigns"]}

for d in defaults:
    if d["id"] not in by_id:
        data["campaigns"].append(d)
    else:
        c = by_id[d["id"]]
        for k, v in d.items():
            if k == "hashes":
                c.setdefault("hashes", [])
            elif k == "keywords":
                c.setdefault("keywords", [])
                for kw in v:
                    if kw not in c["keywords"]:
                        c["keywords"].append(kw)
            else:
                c.setdefault(k, v)

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("campaigns.json OK")
