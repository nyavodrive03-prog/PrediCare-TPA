#!/bin/bash

# =================================================================
# Script de Sauvegarde - PrediCare TPA
# =================================================================
# Ce script extrait la base de données PostgreSQL (conteneur predicare_db)
# et la sauvegarde dans un fichier horodaté dans le dossier ./backups/
# =================================================================

set -e # Arrête le script en cas d'erreur

DB_USER="predicare"
DB_NAME="predicare_db"
CONTAINER_NAME="predicare_db"
BACKUP_DIR="./backups"

# 1. Création du dossier de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# 2. Génération du nom de fichier avec la date et l'heure
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/predicare_backup_$TIMESTAMP.sql"

echo "Début de la sauvegarde de la base de données '$DB_NAME'..."

# 3. Exécution de pg_dump à l'intérieur du conteneur
# -T désactive l'allocation d'un pseudo-TTY pour que le fichier soit propre
if docker compose exec -T $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > "$BACKUP_FILE"; then
    echo "✅ Sauvegarde réussie !"
    echo "📁 Fichier créé : $BACKUP_FILE"
    
    # 4. (Optionnel) Compresser la sauvegarde pour gagner de la place
    gzip "$BACKUP_FILE"
    echo "🗜️  Fichier compressé : $BACKUP_FILE.gz"
else
    echo "❌ Erreur lors de la sauvegarde."
    exit 1
fi