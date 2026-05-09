from pathlib import Path

p = Path("sales_orchestrator.py")
txt = p.read_text(encoding="utf-8-sig")

# 1) Ajouter helpers si absents
helpers = r'''
def asks_opening_hours(msg: str) -> bool:
    m = normalize(msg)
    checks = [
        "heure de fermeture", "vous fermez", "fermeture", "fermez a quelle heure",
        "fermez à quelle heure", "jusqu a quelle heure", "jusqu à quelle heure",
        "heure", "horaires", "ouvert jusqu"
    ]
    return any(x in m for x in checks)

def food_opening_hours_reply() -> str:
    return cfg().get("food", {}).get(
        "closing_time_reply",
        "On ferme à 22h. Envoyez le plat choisi + votre quartier + votre numéro pour commander."
    )

def non_food_opening_hours_reply() -> str:
    return cfg().get("non_food", {}).get(
        "opening_hours_reply",
        "Nous fermons à 22h. Vous souhaitez être livré ou venir récupérer chez nous ?"
    )

def food_pointe_noire_reply() -> str:
    return cfg().get("food", {}).get(
        "pointe_noire_reply",
        "Désolé, on ne livre pas sur Pointe-Noire. Livraison uniquement sur Brazzaville."
    )
'''

if "def asks_opening_hours" not in txt:
    insert_before = "def food_combined_reply(message: str) -> str:"
    txt = txt.replace(insert_before, helpers + "\n" + insert_before)

# 2) Dans food_combined_reply, remplacer le bloc Pointe-Noire
old_food_pn = '''    if asks_pointe_noire(message):
        parts.append(
            "Concernant Pointe-Noire : pour les plats, on fonctionne surtout en livraison locale selon zone. "
            "Envoyez votre quartier exact pour confirmer si la livraison est possible."
        )'''

new_food_pn = '''    if asks_pointe_noire(message):
        parts.append(food_pointe_noire_reply())'''

txt = txt.replace(old_food_pn, new_food_pn)

# 3) Ajouter heure de fermeture au début de food_combined_reply
needle = '''    parts = []'''
replacement = '''    parts = []

    if asks_opening_hours(message):
        parts.append(food_opening_hours_reply())'''

# Remplacer seulement la première occurrence après def food_combined_reply
idx = txt.find("def food_combined_reply")
if idx != -1:
    after = txt[idx:]
    if "if asks_opening_hours(message):" not in after.split("def global_combined_reply")[0]:
        after = after.replace(needle, replacement, 1)
        txt = txt[:idx] + after

# 4) Dans global_combined_reply, ajouter heure hors nourriture avant Pointe-Noire
old_global = '''    # 3) Pointe-Noire hors nourriture.
    if asks_pointe_noire(message):
        return {
            "reply": pointe_noire_non_food_reply(),
            "confidence": 0.93,
            "intent": "sales_pointe_noire_non_food",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_city"}
        }'''

new_global = '''    # 3) Heure de fermeture hors nourriture.
    if asks_opening_hours(message):
        return {
            "reply": non_food_opening_hours_reply(),
            "confidence": 0.93,
            "intent": "sales_opening_hours",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_hours"}
        }

    # 4) Pointe-Noire hors nourriture.
    if asks_pointe_noire(message):
        return {
            "reply": pointe_noire_non_food_reply(),
            "confidence": 0.93,
            "intent": "sales_pointe_noire_non_food",
            "safe_to_auto_send": True,
            "debug": {"source": "sales_orchestrator_city"}
        }'''

txt = txt.replace(old_global, new_global)

p.write_text(txt, encoding="utf-8")
print("✅ sales_orchestrator.py patché : heures + Pointe-Noire.")
