import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data["audit_all_visible_messages"] = True
data["precheck_verbose"] = False
data["precheck_rescan_known_after_seconds"] = 3600
data["precheck_rescan_after_seconds"] = 300

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json : audit ON, precheck moins bavard.")
