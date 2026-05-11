from pathlib import Path

p = Path("conversation_guard.py")
txt = p.read_text(encoding="utf-8-sig")

old = '''    exact = {
        "ok", "okay", "d accord", "daccord", "merci", "merci bien",
        "merci beaucoup", "bien recu", "bien reçu", "recu", "reçu",
        "noté", "note", "c est bon", "cest bon", "ca marche",
        "ça marche", "parfait", "cool", "oui", "non merci"
    }'''

new = '''    exact = {
        "ok", "okay", "d accord", "daccord", "d'accord", "merci", "merci bien",
        "merci beaucoup", "bien recu", "bien reçu", "recu", "reçu",
        "noté", "note", "c est bon", "cest bon", "ca marche",
        "ça marche", "parfait", "cool", "oui", "non merci"
    }'''

if old in txt:
    txt = txt.replace(old, new)

# Si le dernier message est un accord, silence même si les anciens messages restent visibles.
txt = txt.replace(
'''    if is_ack_or_note(latest):
        log_human_correction(chat_id, latest, "ack_or_note_no_reply")
        return []''',
'''    if is_ack_or_note(latest):
        log_human_correction(chat_id, latest, "ack_or_note_no_reply")
        return []'''
)

p.write_text(txt, encoding="utf-8")
print("✅ conversation_guard.py : D’accord traité comme silence.")
