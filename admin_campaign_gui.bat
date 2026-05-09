@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python admin_campaign_gui.py
pause
