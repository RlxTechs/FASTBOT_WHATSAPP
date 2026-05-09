@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python label_last_unknown_as_menu.py
pause
