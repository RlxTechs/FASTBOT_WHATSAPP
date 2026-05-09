import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig"))

data["send_automatically"] = True
data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True
data["auto_send_delay_seconds"] = 0.8
data["skip_if_message_box_not_empty"] = True

data["chrome_control"] = {
    "enabled": True,
    "debug_port": 9222,
    "attach_if_available": True,
    "auto_launch_if_not_available": True,
    "use_dedicated_profile": True,
    "dedicated_profile_dir": "chrome_whatsapp_profile",
    "whatsapp_url": "https://web.whatsapp.com/",
    "wait_ready_seconds": 240
}

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("settings.json mis à jour V3")
