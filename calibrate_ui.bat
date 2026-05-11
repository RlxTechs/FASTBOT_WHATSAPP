@echo off
cd /d "%~dp0"
title FASTBOT V11 - Calibrage UI

if not exist ".venv\Scripts\python.exe" (
    echo Creation de l'environnement Python...
    python -m venv .venv
)

echo Verification des dependances...
".venv\Scripts\python.exe" -m pip install --upgrade pyautogui pillow pyperclip selenium

echo.
echo Lancement du calibrage...
".venv\Scripts\python.exe" calibrate_ui.py
pause
