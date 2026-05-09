import json
from pathlib import Path

p = Path("sales_config.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data.setdefault("non_food", {})

data["non_food"]["facebook_no_context_seller_fallback"] = (
    "Bonjour 👋 Oui bien sûr.\n"
    "Dites-moi ce qui vous intéresse exactement, ou envoyez une capture de la pub si possible.\n\n"
    "En ce moment, les articles qui partent vite sont :\n"
    "🔥 TV Smart 32 / 43 / 55 pouces\n"
    "💻 Laptops HP Core i3 / i5 / i7\n"
    "⚡ Groupes électrogènes 5KVA / 7KVA / 8KVA\n"
    "🔌 Stabilisateurs East Point 1000VA / 2000VA / 5000VA\n"
    "🧊 Frigos, congélateurs, splits / climatiseurs\n"
    "📱 iPhones selon stock disponible\n"
    "🖨️ Imprimantes, cartouches, encres, bureautique\n"
    "🍽️ Plats disponibles en livraison : alloco, chawarma, riz, hamburger...\n\n"
    "Vous cherchez plutôt nourriture, électroménager, informatique, TV, iPhone, énergie ou papeterie ?"
)

data["non_food"]["hot_sales_short"] = (
    "Articles populaires en ce moment : TV Smart, laptops HP, groupes électrogènes, stabilisateurs, frigos/congélateurs, "
    "splits, iPhones, imprimantes, papeterie et plats en livraison."
)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("sales_config.json mis à jour V5.4")
