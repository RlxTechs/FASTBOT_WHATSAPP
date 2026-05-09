param(
    [string]$GitHubUser = "RlxTechs",
    [string]$RepoName = "ocg-whatsapp-sales-bot"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $ROOT

if (!(Test-Path ".git")) {
    git init
    git branch -M main
}

$remote = "https://github.com/$GitHubUser/$RepoName.git"

$existing = git remote 2>$null
if ($existing -match "origin") {
    git remote set-url origin $remote
} else {
    git remote add origin $remote
}

Write-Host "Remote configure : $remote"
