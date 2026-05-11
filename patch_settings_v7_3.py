import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data["send_automatically"] = True
data["audit_all_visible_messages"] = True
data["precheck_verbose"] = False
data["block_on_unknown_campaign"] = False
data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True
data["auto_send_delay_seconds"] = 0.8
data["skip_if_message_box_not_empty"] = True

# Tu peux activer ces deux options dans admin_control_gui quand tu veux autonomie totale.
data.setdefault("autonomous_mode_enabled", False)
data.setdefault("auto_scan_unread_chats", False)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json V7.3 stabilisé.")
