import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig"))
data["auto_scan_unread_chats"] = True
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ Auto-scan activé.")
