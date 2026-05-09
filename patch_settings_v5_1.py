import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig"))

data["precheck_cache_enabled"] = True
data["precheck_rescan_after_seconds"] = 90
data["precheck_rescan_known_after_seconds"] = 600
data["precheck_verbose"] = True

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("settings.json mis à jour V5.1")
