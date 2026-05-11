from runtime_message_reader import is_auto_greeting_or_ad_card, is_pending_encryption_message
from runtime_priority_rules import try_priority_reply
from bot_core import set_state

chat = "test_v7_2"

set_state(chat, {
    "last_category": "food",
    "last_product_family": "food"
})

tests = [
    "En attente de ce message. Vérifiez votre téléphone. En savoir plus",
    "Pourquoi vous supprimez les messages je peux payer aujourd’hui si vous voulez",
    "Je confirme la commande le paiement sur place ça fera combien",
    "D’accord à 10h je t’appelle",
    "Je peux faire la commande ?"
]

print("AUTO GREETING:", is_auto_greeting_or_ad_card("Publicité de facebook\nAfficher les détails\nBonjour ! Dites-nous comment nous pouvons vous aider.\nSalutation automatique"))
print("PENDING:", is_pending_encryption_message("En attente de ce message. Vérifiez votre téléphone. En savoir plus"))

for msg in tests:
    r = try_priority_reply(msg, msg, chat)
    print("=" * 90)
    print("MSG:", msg)
    print("INTENT:", r.get("intent") if r else None)
    print("REPLY:", r.get("reply") if r else None)
