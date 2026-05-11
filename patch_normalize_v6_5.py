from pathlib import Path

p = Path("bot_core.py")
txt = p.read_text(encoding="utf-8-sig")

if "import unicodedata" not in txt:
    txt = txt.replace("import re", "import re\nimport unicodedata")

old = '''def normalize(s):
    s = (s or "").lower().strip()'''

new = '''def normalize(s):
    s = unicodedata.normalize("NFKC", str(s or ""))
    s = s.lower().strip()'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ normalize exact non trouvé, vérifie bot_core.py")

p.write_text(txt, encoding="utf-8")
print("✅ bot_core.normalize amélioré pour textes stylisés.")
