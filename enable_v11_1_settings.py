import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

# Pause humaine
data["pause_when_user_active"] = True
data["resume_after_user_idle_seconds"] = 5
data["human_pause_poll_seconds"] = 0.5

# Vitesse patrouille
data["poll_seconds"] = 0.8
data["patrol_after_click_wait_seconds"] = 0.8
data["patrol_coordinate_cycle_seconds"] = 2.5
data["patrol_min_seconds_between_same_chat"] = 15

# Autonomie
data["send_automatically"] = True
data["autonomous_mode_enabled"] = True
data["auto_scan_unread_chats"] = True
data["patrol_use_unread_filter"] = True
data["patrol_coordinate_fallback"] = True
data["patrol_changed_chats"] = True
data["patrol_new_rows"] = True

# Sécurité
data["skip_if_message_box_not_empty"] = False
data["audit_all_visible_messages"] = True
data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True

# Relances OFF tant que les réponses ne sont pas 100% stables
data["auto_followup_enabled"] = False

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ settings.json mis à jour V11.1")
print(json.dumps({
    "pause_when_user_active": data["pause_when_user_active"],
    "resume_after_user_idle_seconds": data["resume_after_user_idle_seconds"],
    "poll_seconds": data["poll_seconds"],
    "patrol_min_seconds_between_same_chat": data["patrol_min_seconds_between_same_chat"]
}, ensure_ascii=False, indent=2))
