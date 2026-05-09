@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python check_chrome_control.py
pause
