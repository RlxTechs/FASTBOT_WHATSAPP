# OCG WhatsApp Sales Bot

Assistant local Windows pour automatiser les réponses commerciales WhatsApp Web.

## Fonctions principales

- Réponses WhatsApp automatiques avec Selenium.
- Précheck des cartes Publicité Facebook.
- Reconnaissance des miniatures de pubs.
- Admin graphique pour attribuer les pubs inconnues.
- Réponses groupées aux derniers messages client.
- Mode nourriture : menu direct et livraison uniquement.
- Mode boutique : livraison ou retrait après confirmation.
- Catalogue global : informatique, électroménager, papeterie, bureautique, TV, iPhone, services.
- Build EXE Windows avec PyInstaller.

## Lancer le bot

Dans PowerShell :

    .\start_bot.bat

## Ouvrir l'admin graphique

    .\admin_sales_gui.bat

## Construire l'EXE

    .\scripts\build_exe.ps1 -Version "5.3.0"

## Données privées non publiées

Les conversations clients, captures, logs et profils Chrome sont exclus par .gitignore.
