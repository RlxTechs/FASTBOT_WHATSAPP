@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat 2>nul
python admin_control_gui.py
pause
