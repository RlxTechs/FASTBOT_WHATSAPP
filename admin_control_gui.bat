@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python admin_control_gui.py
pause
