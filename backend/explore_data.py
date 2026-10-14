import pandas as pd
import os

print("=" * 70)
print("EXPLORATION DES DONNÉES PREDICARE TPA")
print("=" * 70)

# Chemins à l'intérieur du conteneur
DATASET_DIR = "/data/raw/dataset"
LABELS_DIR = "/data/raw/labels"

def explore_file(filepath, name):
    print("\n" + "=" * 70)
    print(f"FICHIER : {name}")
    print("=" * 70)
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier introuvable : {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath)
        print(f"Nombre de lignes      : {df.shape[0]:,}")
        print(f"Nombre de colonnes    : {df.shape[1]}")
        print(f"\nColonnes :")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nTypes de données :")
        print(df.dtypes)
        
        print(f"\nValeurs manquantes :")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            print(missing)
        else:
            print("  Aucune valeur manquante")
        
        print(f"\nAperçu (3 premières lignes) :")
        print(df.head(3).to_string())
        
        return df
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

# ============================================
# 1. Fichiers les plus importants
# ============================================

print("\n\n>>> 1. FACTURES + LABELS DE FRAUDE")

df_factures = explore_file(f"{DATASET_DIR}/factures.csv", "factures.csv")
df_labels = explore_file(f"{LABELS_DIR}/labels_fraude.csv", "labels_fraude.csv")

print("\n\n>>> 2. LIGNES DE FACTURE")
df_lignes = explore_file(f"{DATASET_DIR}/lignes_facture.csv", "lignes_facture.csv")

print("\n\n>>> 3. ORDONNANCES")
df_ordos = explore_file(f"{DATASET_DIR}/ordonnances.csv", "ordonnances.csv")
df_ordos_lignes = explore_file(f"{DATASET_DIR}/ordonnance_lignes.csv", "ordonnance_lignes.csv")

print("\n\n>>> 4. PRESTATAIRES")
df_prestataires = explore_file(f"{DATASET_DIR}/prestataires.csv", "prestataires.csv")
df_grille = explore_file(f"{DATASET_DIR}/grille_tarifaire.csv", "grille_tarifaire.csv")

print("\n\n" + "=" * 70)
print("EXPLORATION TERMINÉE")
print("=" * 70)