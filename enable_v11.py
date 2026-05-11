import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data["send_automatically"] = True
data["autonomous_mode_enabled"] = True
data["auto_scan_unread_chats"] = True
data["patrol_use_unread_filter"] = True
data["patrol_coordinate_fallback"] = True
data["patrol_changed_chats"] = True
data["patrol_new_rows"] = True
data["patrol_recent_limit"] = 8
data["patrol_min_seconds_between_same_chat"] = 8
data["patrol_coordinate_cycle_seconds"] = 3
data["patrol_after_click_wait_seconds"] = 1.0
data["skip_if_message_box_not_empty"] = False

data["audit_all_visible_messages"] = True
data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True
data["auto_send_delay_seconds"] = 0.8
data["block_on_unknown_campaign"] = False

data.setdefault("auto_followup_enabled", False)
data.setdefault("followup_after_minutes_1", 20)
data.setdefault("followup_after_minutes_2", 60)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("✅ V11 activé.")
print(json.dumps(data, ensure_ascii=False, indent=2))
