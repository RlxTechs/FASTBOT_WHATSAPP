import time
from selenium.webdriver.common.by import By

def open_next_unread_chat(driver):
    """
    Essaie d’ouvrir une conversation non lue dans la colonne gauche WhatsApp Web.
    WhatsApp change souvent ses sélecteurs, donc on reste prudent.
    Retourne True si une conversation a été ouverte.
    """
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        if not rows:
            rows = driver.find_elements(By.CSS_SELECTOR, "div[aria-label*='Chat'], div[aria-label*='conversation']")

        for row in rows:
            try:
                if not row.is_displayed():
                    continue

                text = (row.text or "").strip().lower()
                aria = (row.get_attribute("aria-label") or "").strip().lower()
                html = (row.get_attribute("innerHTML") or "").lower()

                unread_signal = (
                    "non lu" in text
                    or "non lus" in text
                    or "unread" in text
                    or "non lu" in aria
                    or "unread" in aria
                    or "aria-label=\"1\"" in html
                    or "unread" in html
                )

                # Évite de cliquer sur un simple bouton/menu.
                has_name = len(text) > 3

                if unread_signal and has_name:
                    row.click()
                    time.sleep(1.0)
                    return True
            except Exception:
                continue
    except Exception:
        return False

    return False
