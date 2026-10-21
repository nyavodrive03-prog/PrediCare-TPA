import pandas as pd
from sqlalchemy import create_engine
import os

# Connexion depuis l’intérieur du conteneur
DATABASE_URL = "postgresql://predicare:predicare123@db:5432/predicare_db"
engine = create_engine(DATABASE_URL)

# Dossiers des CSV (corrigés : les fichiers sont dans dataset/, les labels dans labels/)
DATA_DIR = "/data/raw/dataset"
LABELS_DIR = "/data/raw/labels"

files = {
    "assures.csv": "assures",
    "contrats.csv": "contrats",
    "factures.csv": "factures",
    "garanties.csv": "garanties",
    "grille_tarifaire.csv": "grille_tarifaire",
    "identites_pii.csv": "identites_pii",
    "lignes_facture.csv": "lignes_facture",
    "ordonnances.csv": "ordonnances",
    "ordonnance_lignes.csv": "ordonnances_lignes",
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

# Chargement des labels de fraude (fichier séparé)
labels_path = os.path.join(LABELS_DIR, "labels_fraude.csv")
if os.path.exists(labels_path):
    print(f"Chargement de labels_fraude.csv → table labels_fraude")
    try:
        df = pd.read_csv(labels_path)
        df.to_sql("labels_fraude", engine, if_exists="replace", index=False)
        print(f"  → {len(df)} lignes chargées")
    except Exception as e:
        print(f"  Erreur sur labels_fraude.csv : {e}")
else:
    print("  Fichier manquant : labels_fraude.csv")

print("\nChargement terminé !")