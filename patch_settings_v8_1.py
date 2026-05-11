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

# À activer dans admin_control_gui quand tu es prêt.
data.setdefault("autonomous_mode_enabled", False)
data.setdefault("auto_scan_unread_chats", False)
data.setdefault("patrol_recent_chats", False)
data.setdefault("patrol_recent_limit", 8)

# Relances désactivées par défaut.
data.setdefault("auto_followup_enabled", False)
data.setdefault("followup_after_minutes_1", 20)
data.setdefault("followup_after_minutes_2", 60)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json V8.1 prêt.")
