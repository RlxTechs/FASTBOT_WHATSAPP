from pathlib import Path

p = Path("admin_control_gui.py")
txt = p.read_text(encoding="utf-8-sig")

# Ajouter defaults si absents
txt = txt.replace(
    '"auto_followup_enabled": False,',
    '"auto_followup_enabled": False,\n    "pause_when_user_active": True,'
)

# Ajouter checkbox dans sécurité si absent
if "pause_when_user_active" not in txt.split("def build")[1]:
    marker = 'self.add_bool(safety, "auto_followup_enabled", "Relances automatiques", "À activer seulement quand le bot est stable.")'
    insert = marker + '\n        self.add_bool(safety, "pause_when_user_active", "Pause quand je touche souris/clavier", "Le bot attend ton inactivité avant de reprendre.")'
    txt = txt.replace(marker, insert)

# Ajouter champs numériques si absents
if "resume_after_user_idle_seconds" not in txt:
    txt = txt.replace(
        '("followup_after_minutes_2", "Relance 2 après minutes")',
        '("followup_after_minutes_2", "Relance 2 après minutes"),\n            ("resume_after_user_idle_seconds", "Reprise après inactivité sec"),\n            ("poll_seconds", "Vitesse boucle sec")'
    )

p.write_text(txt, encoding="utf-8")
print("✅ admin_control_gui.py : options pause/vitesse ajoutées.")
