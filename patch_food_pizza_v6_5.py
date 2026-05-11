from pathlib import Path

p = Path("food_order_guard.py")
txt = p.read_text(encoding="utf-8-sig")

if "from manual_approval import create_pending_order" not in txt:
    txt = txt.replace(
        "from bot_core import normalize, get_state",
        "from bot_core import normalize, get_state\nfrom manual_approval import create_pending_order"
    )

# Ajouter helpers pizza
helpers = r'''
def is_pizza_message(text: str) -> bool:
    m = normalize(text)
    return any(x in m for x in ["pizza", "piza", "pitsa", "durum", "dürum", "kebab", "margherita", "riene"])

def pizza_menu_reply() -> str:
    return (
        "Oui, voici le menu Pizza / Dürum disponible selon stock 🍕👇\n\n"
        "• Dürum Margherita — 5.000 F / 5.500 F\n"
        "• Dürum Riene — 6.000 F / 6.500 F\n"
        "• Dürum Kebab — 6.000 F / 6.500 F\n\n"
        "La disponibilité dépend du moment et du livreur. 🚚\n"
        "Envoyez le choix voulu + votre quartier + votre numéro, et je confirme rapidement."
    )

def pizza_waiting_reply(chat_id: str, combined_message: str, zone_label: str = "") -> str:
    create_pending_order(
        chat_id=chat_id,
        order_type="pizza",
        client_message=combined_message,
        zone=zone_label,
        item="Pizza / Dürum"
    )
    return (
        "D’accord, j’ai bien noté pour la pizza 🍕\n"
        "Un instant, je vérifie la disponibilité et le livreur avant de confirmer.\n\n"
        "Je vous reviens rapidement."
    )
'''

if "def is_pizza_message" not in txt:
    txt = txt.replace("def try_food_order_guard", helpers + "\n\ndef try_food_order_guard")

# Ajouter priorité pizza au début de try_food_order_guard après le début de fonction
old = '''def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    if has_non_food_words(latest_message) and not is_food_context(chat_id):
        return None'''

new = '''def try_food_order_guard(combined_message: str, latest_message: str, chat_id: str = "default") -> Optional[Dict[str, Any]]:
    # V6.5 : Pizza = menu + validation manuelle avant confirmation.
    if is_pizza_message(combined_message):
        zone = detect_zone(combined_message)

        # Si le client donne juste “pizza”, on envoie le menu d’abord.
        if not zone and len(normalize(combined_message).split()) <= 6:
            return {
                "reply": pizza_menu_reply(),
                "confidence": 0.97,
                "intent": "pizza_menu_request",
                "safe_to_auto_send": True,
                "_state_patch": {
                    "last_category": "food",
                    "last_product_family": "pizza",
                    "last_product_query": "Pizza / Dürum"
                },
                "_media_bundle_ids": ["pizza", "pizza_durum_menu"],
                "debug": {"source": "food_order_guard", "case": "pizza_menu"}
            }

        # Si adresse / zone ou question “c’est bon ?” : validation manuelle.
        return {
            "reply": pizza_waiting_reply(chat_id, combined_message, zone.get("label", "") if zone else ""),
            "confidence": 0.96,
            "intent": "pizza_manual_availability_needed",
            "safe_to_auto_send": True,
            "_state_patch": {
                "last_category": "food",
                "last_product_family": "pizza",
                "last_product_query": "Pizza / Dürum"
            },
            "_no_media": True,
            "debug": {"source": "food_order_guard", "case": "pizza_manual_check"}
        }

    if has_non_food_words(latest_message) and not is_food_context(chat_id):
        return None'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Début try_food_order_guard non trouvé exactement.")

p.write_text(txt, encoding="utf-8")
print("✅ food_order_guard.py corrigé pour pizza + validation manuelle.")
