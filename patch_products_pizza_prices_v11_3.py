import json
from pathlib import Path

p = Path("products.json")

if p.exists():
    data = json.loads(p.read_text(encoding="utf-8-sig"))
else:
    data = {"categories": [], "products": []}

data.setdefault("categories", [])
data.setdefault("products", [])

if not any(str(c.get("id", "")).lower() == "pizza" for c in data["categories"] if isinstance(c, dict)):
    data["categories"].append({
        "id": "pizza",
        "name": "Pizza / Dürum",
        "label": "Pizza / Dürum",
        "icon": "🍕"
    })

products = data["products"]
pizza = None

for product in products:
    if product.get("id") == "pizza_durum_menu":
        pizza = product
        break

if pizza is None:
    pizza = {
        "id": "pizza_durum_menu",
        "title": "Menu Pizza / Dürum",
        "subtitle": "Pizzas disponibles selon stock et livreur",
        "categoryId": "pizza"
    }
    products.append(pizza)

pizza.update({
    "title": "Menu Pizza / Dürum",
    "subtitle": "Pizzas disponibles selon stock et livreur",
    "categoryId": "pizza",
    "tag": "pizza, durum, dürum, restaurant, nourriture, poulet, margherita, riene, kebab",
    "description": "Menu pizza/dürum. Disponibilité à confirmer avant validation de commande.",
    "basePrice": 6000,
    "price": 6000,
    "availability": "À confirmer selon disponibilité",
    "defaultImage": "assets/food/pizza/pizza.jpg",
    "gallery": [
        "assets/food/pizza/pizza1.jpg",
        "assets/food/pizza/pizza2.jpg",
        "assets/food/pizza/pizza3.jpg"
    ],
    "variants": [
        {
            "name": "Dürum Poulet",
            "price": 6000,
            "images": ["assets/food/pizza/poulet.jpg"]
        },
        {
            "name": "Dürum Margherita",
            "price": 7000,
            "images": ["assets/food/pizza/margherita.jpg"]
        },
        {
            "name": "Dürum Riene",
            "price": 8000,
            "images": ["assets/food/pizza/riene.jpg"]
        },
        {
            "name": "Dürum Kebab",
            "price": 9000,
            "images": ["assets/food/pizza/kebab.jpg"]
        }
    ]
})

Path("assets/food/pizza").mkdir(parents=True, exist_ok=True)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("✅ products.json mis à jour avec les nouveaux prix pizza.")
