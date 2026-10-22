#!/bin/bash

# =================================================================
# Script de Restauration - PrediCare TPA
# =================================================================
# Ce script restaure une sauvegarde SQL dans la base de données.
# Usage : ./scripts/restore.sh <chemin_du_fichier.sql>
# =================================================================

set -e

DB_USER="predicare"
DB_NAME="predicare_db"
CONTAINER_NAME="predicare_db"

# 1. Vérification de l'argument
if [ -z "$1" ]; then
    echo "❌ Erreur : Vous devez fournir un fichier de sauvegarde."
    echo "Usage : ./scripts/restore.sh ./backups/mon_fichier.sql"
    exit 1
fi

INPUT_FILE=$1

# 2. Vérification de l'existence du fichier
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Erreur : Le fichier '$INPUT_FILE' est introuvable."
    exit 1
fi

# Si le fichier est compressé (.gz), on le décompresse temporairement
if [[ "$INPUT_FILE" == *.gz ]]; then
    echo "Décompression de $INPUT_FILE..."
    gunzip -c "$INPUT_FILE" > temp_restore.sql
    INPUT_FILE="temp_restore.sql"
fi

echo "⚠️  ATTENTION : Cette action va ÉCRASER la base de données actuelle '$DB_NAME'."
read -p "Êtes-vous sûr de vouloir continuer ? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "Restauration annulée."
    exit 1
fi

echo "Début de la restauration..."
echo "1/2 - Nettoyage de la base de données existante..."
# On supprime le schéma public et on le recrée pour repartir à zéro
docker compose exec -T $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "2/2 - Insertion des données depuis $INPUT_FILE (cela peut prendre quelques minutes)..."
if docker compose exec -T $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME < "$INPUT_FILE"; then
    echo "✅ Restauration terminée avec succès !"
else
    echo "❌ Erreur lors de la restauration."
    exit 1
fi

# Nettoyage du fichier temporaire si on a décompressé
if [ -f "temp_restore.sql" ]; then
    rm temp_restore.sql
fi