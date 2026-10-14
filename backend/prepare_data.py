import pandas as pd
import os

print("Préparation des données pour le modèle de fraude...")

DATASET_DIR = "/data/raw/dataset"
LABELS_DIR = "/data/raw/labels"
PROCESSED_DIR = "/data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

# 1. Charger les fichiers principaux
factures = pd.read_csv(f"{DATASET_DIR}/factures.csv")
labels = pd.read_csv(f"{LABELS_DIR}/labels_fraude.csv")

print(f"Factures : {factures.shape}")
print(f"Labels   : {labels.shape}")

# 2. Fusionner sur facture_id
df = factures.merge(labels, on="facture_id", how="left")

print(f"Après fusion : {df.shape}")

# 3. Vérifier le taux de fraude
fraude_rate = df["est_fraude"].mean() * 100
print(f"\nTaux de fraude : {fraude_rate:.2f}%")
print(df["est_fraude"].value_counts())

# 4. Supprimer les colonnes interdites (fuite de données)
colonnes_interdites = [
    "statut",
    "motif_rejet",
    "montant_pris_en_charge",
    "date_traitement"
]

df = df.drop(columns=colonnes_interdites, errors="ignore")
print(f"\nColonnes après suppression des fuites : {list(df.columns)}")

# 5. Sauvegarder la version de base
output_path = f"{PROCESSED_DIR}/factures_avec_labels.csv"
df.to_csv(output_path, index=False)
print(f"\nFichier sauvegardé : {output_path}")

print("\nPréparation de base terminée avec succès.")