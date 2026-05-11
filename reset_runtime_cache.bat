@echo off
cd /d "%~dp0"
echo === RESET FASTBOT V11 ===
del /f /q handled_incoming.json 2>nul
del /f /q audit_seen.json 2>nul
del /f /q patrol_state.json 2>nul
del /f /q force_precheck.flag 2>nul
echo Caches nettoyes.
pause
