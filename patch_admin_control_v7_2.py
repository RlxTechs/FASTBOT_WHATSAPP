from pathlib import Path

p = Path("admin_control_gui.py")
txt = p.read_text(encoding="utf-8-sig")

txt = txt.replace(
    '"precheck_verbose": False,',
    '"precheck_verbose": False,\n    "block_on_unknown_campaign": False,'
)

needle = '''self.add_bool(root, "precheck_verbose", "Afficher tous les prechecks", "À désactiver si les logs deviennent trop bavards.")'''

insert = '''self.add_bool(root, "precheck_verbose", "Afficher tous les prechecks", "À désactiver si les logs deviennent trop bavards.")
        self.add_bool(root, "block_on_unknown_campaign", "Bloquer si pub inconnue", "OFF recommandé : le bot continue à répondre si le message client est clair.")'''

if needle in txt and "block_on_unknown_campaign" not in txt.split("def build")[1]:
    txt = txt.replace(needle, insert)

p.write_text(txt, encoding="utf-8")
print("✅ admin_control_gui.py mis à jour.")
