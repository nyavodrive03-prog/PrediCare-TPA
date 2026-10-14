import pandas as pd
from sqlalchemy import create_engine
import os

# Connexion depuis l’intérieur du conteneur
DATABASE_URL = "postgresql://predicare:predicare123@db:5432/predicare_db"
engine = create_engine(DATABASE_URL)

# Dossier des CSV
DATA_DIR = "/data/raw"

files = {
    "assures.csv": "assures",
    "contrats.csv": "contrats",
    "factures.csv": "factures",
    "garanties.csv": "garanties",
    "grille_tarifaire.csv": "grille_tarifaire",
    "identites_pii.csv": "identites_pii",
    "lignes_facture.csv": "lignes_facture",
    "ordonnances.csv": "ordonnances",
    "ordonnances_lignes.csv": "ordonnances_lignes",
    "prestataires.csv": "prestataires",
    "referentiel_actes.csv": "referentiel_actes",
    "referentiel_medicaments.csv": "referentiel_medicaments",
}

print("Début du chargement des données...")

for filename, table_name in files.items():
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        print(f"Chargement de {filename} → table {table_name}")
        try:
            df = pd.read_csv(filepath)
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"  → {len(df)} lignes chargées")
        except Exception as e:
            print(f"  Erreur sur {filename} : {e}")
    else:
        print(f"  Fichier manquant : {filename}")

print("\nChargement terminé !")