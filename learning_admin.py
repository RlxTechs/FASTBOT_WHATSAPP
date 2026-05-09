import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
UNKNOWN = BASE / "unknown_messages.jsonl"
INDEX = BASE / "unknown_messages_index.json"
PATTERNS = BASE / "intent_patterns.json"
TEMPLATES = BASE / "response_templates.json"

def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def read_unknowns():
    rows = []
    if not UNKNOWN.exists():
        return rows
    for line in UNKNOWN.read_text(encoding="utf-8-sig").splitlines():
        try:
            row = json.loads(line)
            rows.append(row)
        except Exception:
            pass
    return rows

def list_waiting():
    index = load_json(INDEX, {})
    rows = read_unknowns()
    waiting = []

    for r in rows:
        h = r.get("hash")
        st = index.get(h, {}).get("status", r.get("status", "waiting_learning"))
        if st == "waiting_learning":
            waiting.append(r)

    return waiting

def list_intents(patterns):
    print("\nIntentions disponibles :")
    intents = patterns.get("intents", [])
    for i, item in enumerate(intents, start=1):
        print(f"{i}. {item.get('id')} — {item.get('label')}")
    print("N. Créer une nouvelle intention")
    return intents

def create_intent():
    print("\nCréation d'une nouvelle intention")
    iid = input("ID sans espace, ex: prix_stabilisateur, demande_catalogue : ").strip().lower().replace(" ", "_")
    label = input("Nom lisible : ").strip()
    template_id = iid

    response = input("Réponse commerciale à envoyer pour cette intention : ").strip()
    if not response:
        response = "Merci pour votre message. Envoyez plus de détails pour qu’on vous confirme rapidement."

    keywords = input("Mots-clés séparés par virgule : ").strip()
    kws = [x.strip() for x in keywords.split(",") if x.strip()]

    intent = {
        "id": iid,
        "label": label,
        "priority": 75,
        "threshold": 3,
        "safe_to_auto_send": True,
        "template": template_id,
        "patterns": [],
        "keywords": kws,
        "examples": []
    }

    return intent, template_id, response

def add_example_to_intent(intent, message):
    examples = intent.setdefault("examples", [])
    if message not in examples:
        examples.append(message)

    add_kw = input("Ajouter des mots-clés pour reconnaître ce cas ? Sépare par virgule ou laisse vide : ").strip()
    if add_kw:
        kws = intent.setdefault("keywords", [])
        for k in [x.strip() for x in add_kw.split(",") if x.strip()]:
            if k not in kws:
                kws.append(k)

    add_pat = input("Ajouter un pattern regex simple ? Laisse vide si tu ne sais pas : ").strip()
    if add_pat:
        pats = intent.setdefault("patterns", [])
        if add_pat not in pats:
            pats.append(add_pat)

def mark_learned(h):
    index = load_json(INDEX, {})
    index.setdefault(h, {})
    index[h]["status"] = "learned"
    save_json(INDEX, index)

def main():
    print("=" * 72)
    print("OCG Bot V4.3 — Admin apprentissage des messages inconnus")
    print("=" * 72)

    waiting = list_waiting()
    if not waiting:
        print("Aucun message inconnu à classer pour le moment.")
        return

    for i, r in enumerate(waiting[:40], start=1):
        print(f"\n{i}. [{r.get('reason')}] {r.get('message')}")
        print(f"   hash={r.get('hash')} | intent={r.get('result_intent')} | conf={r.get('result_confidence')}")

    choice = input("\nChoisis le numéro du message à apprendre : ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > min(40, len(waiting)):
        print("Choix invalide.")
        return

    row = waiting[int(choice) - 1]
    message = row.get("message", "")
    h = row.get("hash", "")

    patterns = load_json(PATTERNS, {"version": "4.3", "default_threshold": 4, "intents": []})
    templates = load_json(TEMPLATES, {"version": "4.3", "templates": {}})

    intents = list_intents(patterns)
    ichoice = input("\nChoisis une intention existante ou tape N pour nouvelle : ").strip()

    if ichoice.lower() == "n":
        intent, template_id, response = create_intent()
        intent["examples"].append(message)
        patterns.setdefault("intents", []).append(intent)
        templates.setdefault("templates", {})[template_id] = response
    else:
        if not ichoice.isdigit() or int(ichoice) < 1 or int(ichoice) > len(intents):
            print("Choix invalide.")
            return
        intent = intents[int(ichoice) - 1]
        add_example_to_intent(intent, message)

    save_json(PATTERNS, patterns)
    save_json(TEMPLATES, templates)
    mark_learned(h)

    print("\n✅ Message appris avec succès.")
    print("Relance le bot ou teste avec debug_intelligence.bat.")
    print(f"Message : {message}")

if __name__ == "__main__":
    main()
