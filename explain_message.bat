@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -c "from intent_bank import explain_match; import json; msg=input('Message client: '); print(json.dumps(explain_match(msg), ensure_ascii=False, indent=2))"
pause
