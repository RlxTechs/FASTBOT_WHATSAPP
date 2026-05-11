@echo off
cd /d "%~dp0"

set MSG=%*
if "%MSG%"=="" set MSG=update: save latest bot improvements

echo ==========================================
echo FASTBOT - GIT SAVE + PUSH
echo ==========================================

git config user.name "RlxTechs"
git config user.email "bossedemardochee@gmail.com"

for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=main

git status --short

git status --porcelain > .git_changes.tmp
for %%A in (.git_changes.tmp) do set SIZE=%%~zA

if "%SIZE%"=="0" (
    del .git_changes.tmp
    echo ? Aucun changement a sauvegarder.
    pause
    exit /b 0
)

del .git_changes.tmp

git add .
git commit -m "%MSG%"
git push origin %BRANCH%

echo.
echo ? Projet sauvegarde et pousse sur GitHub.
pause
