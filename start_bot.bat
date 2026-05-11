@echo off
cd /d "%~dp0"
title FASTBOT V11 HARD AUTONOMY
echo ==============================================================
echo FASTBOT V11 HARD AUTONOMY
echo ==============================================================
echo 1. WhatsApp Web doit etre ouvert.
echo 2. Lance calibrate_ui.bat une fois si les clics ne marchent pas.
echo 3. Admin : admin_control_gui.bat
echo ==============================================================
call .venv\Scripts\activate.bat 2>nul
python main_v11.py
pause
