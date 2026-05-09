param(
    [string]$Message = "chore: update OCG WhatsApp Sales Bot",
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git n'est pas installé ou n'est pas dans le PATH."
    exit 1
}

if (!(Test-Path ".git")) {
    git init
    git branch -M main
}

git add .
git commit -m $Message

if ($Push) {
    git push -u origin main
}
