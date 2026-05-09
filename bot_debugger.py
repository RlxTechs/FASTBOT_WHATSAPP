import json
from pathlib import Path
from bot_core import generate_reply, STATE_PATH

BASE_DIR = Path(__file__).resolve().parent

def reset_test_state():
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        data.pop("debug_test", None)
        STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

tests = [
    "haha",
    "dcdc",
    "je veux un ordinateur",
    "le core i3",
    "core i3",
    "congelateur",
    "congelateurr",
    "frigo",
    "refrigerateur",
    "vous etes situer ou",
    "ou est votre boutique ?",
    "ou est votre magasin ?",
    "ou se trouve votre boutique",
    "ou se trouve votre restaurant ?",
    "restaurant ?",
    "vous faites les livraisons ?",
    "livrez-vous a domicile ?",
    "je suis a Mougali",
    "Mounkoudo",
    "prix",
    "tv",
    "32 pouces",
    "vous n'avez pas la marque Huawei ?",
    "marque LG",
    "Je veux une television smart",
    "Je veux une television LG 32 pouces",
    "combien la livraison ?",
    "iphone 13 pro max prix",
    "je veux commander",
    "comment payer ?"
]

reset_test_state()

print("=" * 80)
print("DEBUGGER BOT V2 — tests automatiques")
print("=" * 80)

for msg in tests:
    result = generate_reply(msg, chat_id="debug_test")
    print("\nCLIENT :", msg)
    print("INTENT :", result["intent"], "| CONF :", result["confidence"], "| SAFE :", result["safe_to_auto_send"])
    print("RÉPONSE :")
    print(result["reply"])
    print("-" * 80)

print("\n✅ Debug terminé.")
print("Regarde aussi : debug_logs.jsonl, conversations_state.json, conversations_log.jsonl")
