# Sauvegarde de la base PrediCare (format PostgreSQL compresse).
# Usage : powershell -ExecutionPolicy Bypass -File ops\sauvegarde.ps1
# Les 7 dernieres sauvegardes sont conservees dans le dossier "sauvegardes".
param(
    [string]$Dossier = "sauvegardes",
    [int]$Garder = 7
)
$ErrorActionPreference = "Continue"
Set-Location (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force -Path $Dossier | Out-Null

$horodatage = Get-Date -Format "yyyyMMdd_HHmmss"
$fichier = Join-Path $Dossier "predicare_$horodatage.dump"

docker compose exec -T db sh -c "pg_dump -U postgres -Fc predicare > /tmp/sauvegarde.dump"
if ($LASTEXITCODE -ne 0) { throw "pg_dump a echoue (la base est-elle demarree ?)" }

docker compose cp db:/tmp/sauvegarde.dump $fichier
if ($LASTEXITCODE -ne 0) { throw "Copie de la sauvegarde impossible" }

docker compose exec -T db rm -f /tmp/sauvegarde.dump

Get-ChildItem $Dossier -Filter "predicare_*.dump" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip $Garder |
    Remove-Item -Force

Write-Host "Sauvegarde creee : $fichier"
