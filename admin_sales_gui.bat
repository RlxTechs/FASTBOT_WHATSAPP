@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python admin_sales_gui.py
pause
