import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data["send_automatically"] = True
data["audit_all_visible_messages"] = True
data["precheck_verbose"] = False
data["block_on_unknown_campaign"] = False

# Le bot répond quand TU es dans la conversation.
# Pour qu'il aille lui-même dans les non-lus, active depuis admin_control_gui.
data.setdefault("autonomous_mode_enabled", False)
data.setdefault("auto_scan_unread_chats", False)

data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json corrigé V7.2.")
