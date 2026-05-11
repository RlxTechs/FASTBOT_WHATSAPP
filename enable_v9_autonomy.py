import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

# Envoi
data["send_automatically"] = True
data["confidence_required"] = 0.88
data["auto_send_only_safe"] = True
data["auto_send_delay_seconds"] = 0.8

# Autonomie
data["autonomous_mode_enabled"] = True
data["auto_scan_unread_chats"] = True

# Nouveau système V9 : ne dépend pas seulement du badge non lu
data["patrol_changed_chats"] = True
data["patrol_new_rows"] = True
data["patrol_recent_chats"] = False
data["patrol_recent_limit"] = 8
data["patrol_min_seconds_between_same_chat"] = 12
data["patrol_verbose"] = True

# Pour que le bot ne bloque pas à cause d’un vieux brouillon
# En mode autonome, il doit pouvoir nettoyer le champ.
data["skip_if_message_box_not_empty"] = False

# Logs
data["audit_all_visible_messages"] = True
data["precheck_verbose"] = False
data["block_on_unknown_campaign"] = False

# Relances désactivées au début, à activer après stabilité
data.setdefault("auto_followup_enabled", False)
data.setdefault("followup_after_minutes_1", 20)
data.setdefault("followup_after_minutes_2", 60)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("✅ settings.json V9 activé.")
print("Mode autonome :", data["autonomous_mode_enabled"])
print("Scan non-lus :", data["auto_scan_unread_chats"])
print("Détection changement aperçu :", data["patrol_changed_chats"])
print("Ne bloque pas brouillon :", not data["skip_if_message_box_not_empty"])
