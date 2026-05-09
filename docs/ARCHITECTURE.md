# Architecture

Flux :

WhatsApp Web
-> Selenium
-> Précheck Facebook
-> Détection miniature pub
-> Contexte campagne
-> Lecture messages récents
-> Sales orchestrator
-> Smart reply
-> Envoi WhatsApp

Modules importants :

- main.py : boucle principale WhatsApp.
- campaign_context.py : détection des cartes Facebook.
- sales_orchestrator.py : analyse des messages groupés.
- smart_reply.py : logique commerciale.
- bot_core.py : moteur catalogue.
- admin_sales_gui.py : admin graphique.
