import json
from pathlib import Path

p = Path("products.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {"products": [], "categories": []}

data.setdefault("categories", [])
data.setdefault("products", [])

# Ajouter catégorie si absente
cats = data["categories"]
if not any(str(c.get("id", "")).lower() == "pizza" for c in cats if isinstance(c, dict)):
    cats.append({
        "id": "pizza",
        "name": "Pizza / Dürum",
        "label": "Pizza / Dürum",
        "icon": "🍕"
    })

# Supprimer ancienne version si déjà créée
data["products"] = [x for x in data["products"] if x.get("id") != "pizza_durum_menu"]

pizza_product = {
    "id": "pizza_durum_menu",
    "title": "Menu Pizza / Dürum",
    "subtitle": "Pizzas disponibles selon stock et livreur",
    "categoryId": "pizza",
    "tag": "pizza, durum, restaurant, nourriture",
    "description": "Menu pizza/dürum avec marge commerciale incluse. Disponibilité à confirmer avant validation de commande.",
    "basePrice": 5000,
    "availability": "À confirmer selon disponibilité",
    "defaultImage": "assets/food/pizza/pizza.jpg",
    "gallery": [
        "assets/food/pizza/pizza1.jpg",
        "assets/food/pizza/pizza2.jpg",
        "assets/food/pizza/pizza3.jpg"
    ],
    "variants": [
        {
            "name": "Dürum Margherita - Option 1",
            "price": 5000,
            "images": ["assets/food/pizza/margherita1.jpg"]
        },
        {
            "name": "Dürum Margherita - Option 2",
            "price": 5500,
            "images": ["assets/food/pizza/margherita2.jpg"]
        },
        {
            "name": "Dürum Riene - Option 1",
            "price": 6000,
            "images": ["assets/food/pizza/riene1.jpg"]
        },
        {
            "name": "Dürum Riene - Option 2",
            "price": 6500,
            "images": ["assets/food/pizza/riene2.jpg"]
        },
        {
            "name": "Dürum Kebab - Option 1",
            "price": 6000,
            "images": ["assets/food/pizza/kebab1.jpg"]
        },
        {
            "name": "Dürum Kebab - Option 2",
            "price": 6500,
            "images": ["assets/food/pizza/kebab2.jpg"]
        }
    ]
}

data["products"].append(pizza_product)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

Path("assets/food/pizza").mkdir(parents=True, exist_ok=True)

print("✅ Menu pizza ajouté à products.json avec +1.500 F de marge.")
print("📁 Mets tes images pizza dans : assets/food/pizza/")
