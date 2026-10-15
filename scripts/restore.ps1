# scripts/restore.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

if (-not (Test-Path $BackupFile)) {
    Write-Host "Fichier de sauvegarde introuvable : $BackupFile" -ForegroundColor Red
    exit 1
}

Write-Host "ATTENTION : Cette opération va ÉCRASER la base de données actuelle." -ForegroundColor Yellow
$confirm = Read-Host "Es-tu sûr de vouloir continuer ? (y/n)"

if ($confirm -ne "y") {
    Write-Host "Restauration annulée." -ForegroundColor Cyan
    exit 0
}

Write-Host "Restauration en cours..." -ForegroundColor Cyan

Get-Content $BackupFile | docker compose exec -T db psql -U predicare -d predicare_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "Restauration terminée avec succès." -ForegroundColor Green
} else {
    Write-Host "Erreur lors de la restauration !" -ForegroundColor Red
}