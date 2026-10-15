# scripts/backup.ps1
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = ".\backups"
$BackupFile = "$BackupDir\backup_$Date.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "Sauvegarde de la base de données en cours..." -ForegroundColor Cyan

docker compose exec -T db pg_dump -U predicare predicare_db > $BackupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Sauvegarde réussie : $BackupFile" -ForegroundColor Green
} else {
    Write-Host "Erreur lors de la sauvegarde !" -ForegroundColor Red
}