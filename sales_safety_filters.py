import json
import re
from pathlib import Path
from typing import Optional, Dict, Any

from bot_core import normalize

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

SALES_CONFIG_PATH = BASE_DIR / "sales_config.json"

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default
    return default

def cfg():
    return load_json(SALES_CONFIG_PATH, {})

def is_ack_only(message: str) -> bool:
    m = normalize(message)

    if not m:
        return True

    # On bloque seulement les petits messages de confirmation.
    # Exemple bloqué : "ok", "d'accord", "merci", "svp"
    # Exemple non bloqué : "ok je veux commander"
    if len(m.split()) > 5:
        return False

    ack_exact = {
        "d accord",
        "daccord",
        "dac",
        "ok",
        "ok merci",
        "merci",
        "merci beaucoup",
        "merci bien",
        "ca marche",
        "ça marche",
        "c est bon",
        "cest bon",
        "bien recu",
        "bien reçu",
        "recu",
        "reçu",
        "note",
        "noté",
        "parfait",
        "cool",
        "svp",
        "stp",
        "s il vous plait",
        "s il vous plaît",
        "s'il vous plait",
        "s'il vous plaît",
        "sil vous plait",
        "sil vous plaît"
    }

    if m in ack_exact:
        return True

    allowed_words = {
        "d", "accord", "daccord", "ok", "merci", "beaucoup", "bien",
        "recu", "reçu", "note", "noté", "parfait", "cool", "marche",
        "ca", "ça", "svp", "stp", "s", "il", "vous", "plait", "plaît"
    }

    words = set(m.split())
    return bool(words) and words.issubset(allowed_words)

def is_job_request(message: str) -> bool:
    m = normalize(message)

    patterns = [
        r"\bemploi\b",
        r"\btravail\b",
        r"\bjob\b",
        r"\bposte\b",
        r"\bstage\b",
        r"\bstagiaire\b",
        r"\bcv\b",
        r"\brecrut\w*\b",
        r"\bembauch\w*\b",
        r"\bemploye\w*\b",
        r"\bemployé\w*\b",
        r"\bpersonnel\b",
        r"\bvendeur\b",
        r"\bvendeuse\b",
        r"\bserveur\b",
        r"\bserveuse\b",
        r"\bchauffeur\b",
        r"\blivreur\b",
        r"\bvous cherchez.*employ",
        r"\bcherchez.*employ",
        r"\bavez vous besoin.*employ",
        r"\bbesoin.*employ",
        r"\bje cherche.*travail",
        r"\bje cherche.*emploi",
        r"\bje veux travailler",
        r"\btravailler chez vous"
    ]

    return any(re.search(p, m) for p in patterns)

def not_hiring_reply() -> str:
    return cfg().get("hr", {}).get(
        "not_hiring_reply",
        "Bonjour 🙏 Désolé, nous ne recherchons personne pour le moment.\n"
        "Nous n’avons pas de besoin en employés actuellement.\n\n"
        "Merci pour votre compréhension."
    )

def classify_pre_reply(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict]:
    combined_norm = normalize(combined_message)
    latest_norm = normalize(latest_message)
    only_latest = combined_norm == latest_norm

    # Si c’est juste “ok”, “d’accord”, “merci”, “svp” seul → silence.
    # Si le client a envoyé une vraie question avant “svp”, on laisse le cerveau répondre.
    if only_latest and is_ack_only(latest_message):
        return {
            "reply": "",
            "confidence": 0.0,
            "intent": "no_reply_acknowledgement",
            "safe_to_auto_send": False,
            "debug": {
                "source": "sales_safety_filters",
                "reason": "latest message is acknowledgement/polite filler only",
                "latest_message": latest_message
            }
        }

    # Demande d’emploi / recrutement.
    if is_job_request(combined_message):
        return {
            "reply": not_hiring_reply(),
            "confidence": 0.96,
            "intent": "hr_not_hiring",
            "safe_to_auto_send": True,
            "debug": {
                "source": "sales_safety_filters",
                "reason": "employment/recruitment request detected"
            }
        }

    return None
