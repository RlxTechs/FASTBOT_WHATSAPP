import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from app_paths import BASE_DIR
SETTINGS_PATH = BASE_DIR / "settings.json"

def load_settings():
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}

def find_chrome_exe():
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "chrome.exe"

def is_debug_port_open(port=9222):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1.2) as r:
            return r.status == 200
    except Exception:
        return False

def launch_controlled_chrome():
    s = load_settings()
    cc = s.get("chrome_control", {})
    port = int(cc.get("debug_port", 9222))
    url = cc.get("whatsapp_url", "https://web.whatsapp.com/")

    chrome = find_chrome_exe()

    if cc.get("use_dedicated_profile", True):
        profile_dir = BASE_DIR / cc.get("dedicated_profile_dir", "chrome_whatsapp_profile")
    else:
        profile_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data"

    profile_dir.mkdir(parents=True, exist_ok=True)

    args = [
        chrome,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        "--new-window",
        url
    ]

    print("Lancement Chrome contrôlé...")
    print("Profil :", profile_dir)
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for _ in range(25):
        if is_debug_port_open(port):
            print("Chrome contrôlé détecté sur le port", port)
            return True
        time.sleep(0.5)

    return False

def attach_driver():
    s = load_settings()
    cc = s.get("chrome_control", {})
    port = int(cc.get("debug_port", 9222))

    if cc.get("attach_if_available", True) and is_debug_port_open(port):
        print("Connexion à Chrome déjà contrôlé...")
    else:
        if not cc.get("auto_launch_if_not_available", True):
            raise RuntimeError("Chrome contrôlé non disponible. Lance open_whatsapp_controlled.bat d'abord.")
        ok = launch_controlled_chrome()
        if not ok:
            raise RuntimeError("Impossible de lancer ou détecter Chrome contrôlé.")

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        raise RuntimeError(f"Impossible de s'attacher à Chrome contrôlé : {e}")

    return driver

def ensure_whatsapp_tab(driver):
    url = "https://web.whatsapp.com/"

    try:
        handles = driver.window_handles
        for h in handles:
            driver.switch_to.window(h)
            current = driver.current_url or ""
            if "web.whatsapp.com" in current:
                print("Onglet WhatsApp Web trouvé.")
                return
    except Exception:
        pass

    print("Aucun onglet WhatsApp détecté. Ouverture de WhatsApp Web...")
    driver.get(url)

def whatsapp_ready(driver):
    try:
        # Si la zone de saisie existe, une conversation est ouverte
        boxes = driver.find_elements("css selector", "footer div[contenteditable='true']")
        for b in boxes:
            if b.is_displayed():
                return True

        # Si la liste de conversations existe, WhatsApp est au moins connecté
        side = driver.find_elements("css selector", "#side")
        for s in side:
            if s.is_displayed():
                return True
    except Exception:
        pass
    return False

def wait_for_whatsapp_ready(driver):
    s = load_settings()
    cc = s.get("chrome_control", {})
    timeout = int(cc.get("wait_ready_seconds", 240))

    print("Vérification WhatsApp Web...")
    start = time.time()
    warned = False

    while time.time() - start < timeout:
        if whatsapp_ready(driver):
            print("WhatsApp Web est prêt.")
            return True

        if not warned and time.time() - start > 8:
            print("Si un QR code s'affiche, scanne-le une seule fois. La session restera enregistrée.")
            warned = True

        time.sleep(1)

    print("WhatsApp Web pas encore prêt. Le bot va continuer, mais ouvre une conversation avant de vendre.")
    return False
