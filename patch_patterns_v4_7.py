import json
from pathlib import Path

p = Path("intent_patterns.json")
data = json.loads(p.read_text(encoding="utf-8-sig"))

for intent in data.get("intents", []):
    if intent.get("id") == "location_question":
        patterns = intent.setdefault("patterns", [])
        additions = [
            "\\bdans quel ville\\b",
            "\\bdans quelle ville\\b",
            "\\bquel ville\\b",
            "\\bquelle ville\\b",
            "\\bemplacement\\b",
            "\\bvous etes situe ou\\b",
            "\\bvous etes situes ou\\b",
            "\\bvous etes dans quel ville\\b",
            "\\bvous etes dans quelle ville\\b"
        ]
        for a in additions:
            if a not in patterns:
                patterns.append(a)

        keywords = intent.setdefault("keywords", [])
        for k in ["ville", "emplacement", "situé", "située", "quelle ville", "quel ville"]:
            if k not in keywords:
                keywords.append(k)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("intent_patterns.json corrigé.")
