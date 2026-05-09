@echo off
echo ==========================================================
echo ATTENTION
echo Cette option ferme Chrome puis le relance en mode controle.
echo Elle utilise ton profil Chrome principal.
echo Sauvegarde tes onglets importants avant de continuer.
echo ==========================================================
pause

taskkill /IM chrome.exe /F >nul 2>&1

set CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe
if not exist "%CHROME%" set CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe
if not exist "%CHROME%" set CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe

start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%LocalAppData%\Google\Chrome\User Data" --profile-directory="Default" --no-first-run --no-default-browser-check https://web.whatsapp.com/

echo Chrome principal relance en mode controle.
echo Maintenant lance start_bot.bat
pause
