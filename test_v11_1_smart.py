from smart_overrides import try_smart_override
from lead_memory import remember_outgoing

chat = "test_v11_1"

# Simuler menu déjà envoyé
remember_outgoing(chat, "Bonjour 👋 Voici notre menu disponible aujourd’hui 🍽️\nAlloco poulet — 2.000 F", "food_menu_sent", True)

tests = [
    "Bonsoir",
    "Je ferai le commande demain si possible",
    "Mais la livraison ça c'est passe comment",
    "A Kintélé vous livrez pour combien ?",
    "Je suis à ouenze",
    "En attente de ce message. Vérifiez votre téléphone. En savoir plus"
]

for t in tests:
    r = try_smart_override(t, t, chat)
    print("=" * 90)
    print("CLIENT:", t)
    print("INTENT:", r.get("intent") if r else None)
    print("REPONSE:")
    print(r.get("reply") if r else None)
