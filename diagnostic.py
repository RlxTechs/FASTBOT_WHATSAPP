import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
files = ["products.json", "settings.json", "food_menu.json", "bot_core.py", "main.py"]

print("=== Diagnostic fichiers OCG WhatsApp Bot ===")
for f in files:
    p = BASE / f
    print(f"{f} :", "OK" if p.exists() else "MANQUANT")

try:
    data = json.loads((BASE / "products.json").read_text(encoding="utf-8-sig"))
    products = data.get("products", [])
    categories = data.get("categories", [])
    print("Produits :", len(products))
    print("Catégories :", len(categories))
    empty_images = [x.get("title") for x in products if not x.get("defaultImage")]
    print("Produits sans image principale :", len(empty_images))
except Exception as e:
    print("Erreur products.json :", repr(e))

try:
    s = json.loads((BASE / "settings.json").read_text(encoding="utf-8-sig"))
    print("Ville :", s.get("city"))
    print("WhatsApp :", s.get("whatsapp"))
    print("Mode auto :", s.get("send_automatically"))
    print("Debug :", s.get("debug_enabled"))
except Exception as e:
    print("Erreur settings.json :", repr(e))

print("=== Fin diagnostic ===")
