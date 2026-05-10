import json
from pathlib import Path

p = Path("media_catalog.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {"bundles": []}

data["version"] = "6.2"
data["enabled"] = True
data["send_images_automatically"] = True
data["max_images_per_reply"] = 3
data["strict_mode"] = True

for b in data.get("bundles", []):
    bid = str(b.get("id", "")).lower()
    label = str(b.get("label", "")).lower()
    kws = [str(x).lower() for x in b.get("keywords", [])]

    b.setdefault("active", True)
    b.setdefault("priority", 0)
    b.setdefault("min_score", 15)
    b.setdefault("negative_keywords", [])
    b.setdefault("intents", [])
    b["allow_context_only"] = False
    b["allow_intent_only"] = False

    if "fridge" in bid or "frigo" in bid or "refriger" in bid or "réfrig" in label or "frigo" in label:
        b["min_score"] = 25
        b["allow_context_only"] = False
        b["allow_intent_only"] = False
        b["keywords"] = ["frigo", "réfrigérateur", "refrigerateur", "réfrigérateurs", "refrigerateurs"]
        b["negative_keywords"] = [
            "iphone", "hamburger", "gateau", "gâteau", "menu", "nourriture",
            "ordinateur", "laptop", "tv", "imprimante", "cartouche", "groupe"
        ]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ media_catalog.json sécurisé : bundles frigo stricts.")
