from pathlib import Path

p = Path("intent_bank.py")
txt = p.read_text(encoding="utf-8-sig")

old = "return txt.strip()"
new = "return txt.replace('\\\\n', '\\n').strip()"

if old in txt and "txt.replace('\\\\\\\\n'" not in txt:
    txt = txt.replace(old, new)

p.write_text(txt, encoding="utf-8")
print("intent_bank.py corrigé : les \\\\n deviennent de vrais retours à la ligne.")
