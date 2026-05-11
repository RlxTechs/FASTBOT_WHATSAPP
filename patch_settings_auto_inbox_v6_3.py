import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

# Futur mode automatique. Désactivé pour l’instant, pour éviter qu’il clique partout pendant tes tests.
data["auto_scan_unread_chats"] = False
data["auto_scan_when_idle_seconds"] = 4
data["skip_conversation_ouverte"] = True

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json préparé pour auto inbox futur.")
