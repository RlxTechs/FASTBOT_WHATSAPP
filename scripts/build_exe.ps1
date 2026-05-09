param(
    [string]$Version = "5.3.0"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

Write-Host "=== Build EXE OCG WhatsApp Bot v$Version ==="

if (!(Test-Path ".\.venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\pip.exe install -r requirements-dev.txt

.\.venv\Scripts\python.exe ".\scripts\patch_app_paths.py"

Remove-Item -Recurse -Force ".\build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue

$OUT = ".\release\OCG_WhatsApp_Bot_v$Version"
Remove-Item -Recurse -Force $OUT -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

Write-Host "Compilation bot principal..."
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --console --name "OCG-WhatsApp-Bot" main.py

if (Test-Path ".\admin_sales_gui.py") {
    Write-Host "Compilation admin graphique..."
    .\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name "OCG-Admin-Sales" admin_sales_gui.py
}

Copy-Item ".\dist\OCG-WhatsApp-Bot.exe" "$OUT\OCG-WhatsApp-Bot.exe" -Force

if (Test-Path ".\dist\OCG-Admin-Sales.exe") {
    Copy-Item ".\dist\OCG-Admin-Sales.exe" "$OUT\OCG-Admin-Sales.exe" -Force
}

$DataFiles = @(
    "products.json",
    "sales_config.json",
    "campaigns.json",
    "intent_patterns.json",
    "response_templates.json",
    "fb_context_rules.json",
    "food_menu.json",
    "settings.json",
    "README.md",
    "CHANGELOG.md"
)

foreach ($f in $DataFiles) {
    if (Test-Path $f) {
        Copy-Item $f "$OUT\$f" -Force
    }
}

@"
@echo off
cd /d "%~dp0"
OCG-WhatsApp-Bot.exe
pause
"@ | Set-Content -Encoding ASCII "$OUT\Lancer_Bot.bat"

@"
@echo off
cd /d "%~dp0"
OCG-Admin-Sales.exe
pause
"@ | Set-Content -Encoding ASCII "$OUT\Admin_Graphique.bat"

@"
@echo off
cd /d "%~dp0"
echo force > force_precheck.flag
echo Precheck force. Retourne dans la fenetre du bot.
pause
"@ | Set-Content -Encoding ASCII "$OUT\Force_Precheck.bat"

New-Item -ItemType Directory -Force -Path "$OUT\campaign_captures" | Out-Null
New-Item -ItemType Directory -Force -Path "$OUT\chrome_whatsapp_profile" | Out-Null

Compress-Archive -Path "$OUT\*" -DestinationPath ".\release\OCG_WhatsApp_Bot_v$Version.zip" -Force

Write-Host ""
Write-Host "BUILD TERMINE"
Write-Host "Dossier : $OUT"
Write-Host "ZIP : .\release\OCG_WhatsApp_Bot_v$Version.zip"
