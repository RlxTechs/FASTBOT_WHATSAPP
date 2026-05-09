@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python debug_intelligence.py
pause
