# Restauration de la base PrediCare depuis une sauvegarde.
# Usage : powershell -ExecutionPolicy Bypass -File ops\restauration.ps1 -Fichier sauvegardes\predicare_XXXX.dump
# ATTENTION : la base actuelle est remplacee par le contenu de la sauvegarde.
param(
    [Parameter(Mandatory = $true)][string]$Fichier,
    [switch]$Force
)
$ErrorActionPreference = "Continue"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path $Fichier)) { throw "Fichier introuvable : $Fichier" }
$chemin = (Resolve-Path $Fichier).Path

if (-not $Force) {
    $reponse = Read-Host "La base actuelle sera REMPLACEE par $chemin. Continuer ? (oui/non)"
    if ($reponse -ne "oui") { Write-Host "Restauration annulee."; exit 0 }
}

docker compose stop app
docker compose cp $chemin db:/tmp/restauration.dump
if ($LASTEXITCODE -ne 0) { throw "Copie de la sauvegarde impossible" }

docker compose exec -T db psql -U postgres -d predicare -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec -T db sh -c "pg_restore -U postgres -d predicare --no-owner /tmp/restauration.dump"
if ($LASTEXITCODE -ne 0) {
    Write-Host "pg_restore a signale des avertissements (code $LASTEXITCODE) : verifier les donnees."
}
docker compose exec -T db rm -f /tmp/restauration.dump

docker compose start app
Write-Host "Restauration terminee depuis : $chemin"
