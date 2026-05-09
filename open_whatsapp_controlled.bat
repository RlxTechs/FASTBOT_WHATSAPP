@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -c "from chrome_control import launch_controlled_chrome; launch_controlled_chrome()"
pause
