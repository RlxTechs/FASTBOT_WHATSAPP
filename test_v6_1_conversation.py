from conversation_brain import generate_human_sales_reply
from bot_core import set_state

tests = [
    ("test1", "Bonjour ! Puis-je en savoir plus à ce sujet ?\ns'il vous plaît"),
    ("test1", "Je parle de la nourriture vos prix mon beaucoup attiré"),
    ("test2", "Ok vous faite aussi les gâteaux d'anniversaire"),
    ("test3", "Les iPhone la c'est combien"),
    ("test3", "XR combien"),
    ("test3", "7 plus"),
    ("test3", "Vous acceptez aussi des avence"),
    ("test3", "Mes Le pris"),
    ("test3", "Mes 12 pro max"),
    ("test3", "Ok")
]

# Simuler contexte iPhone après la demande iPhone
set_state("test3", {"last_category": "iphones", "last_product_family": "iphones"})

for chat, msg in tests:
    r = generate_human_sales_reply(msg, chat)
    print("=" * 90)
    print("CHAT:", chat)
    print("CLIENT:")
    print(msg)
    print("INTENT:", r.get("intent"))
    print("CONF:", r.get("confidence"))
    print("RÉPONSE:")
    print(r.get("reply"))
    print("STATE_PATCH:", r.get("_state_patch"))
    print("IMAGES:", r.get("_media_images"))
