@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python admin_pending_orders.py
pause
