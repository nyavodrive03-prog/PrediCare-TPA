import pandas as pd
import numpy as np
from datetime import datetime

print("Feature Engineering v1 - Nettoyage et premières variables")

# Charger le fichier préparé
df = pd.read_csv("/data/processed/factures_avec_labels.csv")

print(f"Données chargées : {df.shape}")

# ==============================================
# 1. Conversion des dates
# ==============================================
date_cols = ["date_soin", "date_facture", "date_reception"]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

print("Dates converties.")

# ==============================================
# 2. Features de base (très utiles)
# ==============================================

# A. Est-ce qu'il y a une ordonnance ?
df["a_ordonnance"] = df["ordonnance_id"].notna().astype(int)

# B. Délai entre soin et facture (en jours)
df["delai_soin_facture"] = (df["date_facture"] - df["date_soin"]).dt.days

# C. Délai entre facture et réception
df["delai_facture_reception"] = (df["date_reception"] - df["date_facture"]).dt.days

# D. Jour de la semaine du soin (0 = lundi, 6 = dimanche)
df["jour_semaine_soin"] = df["date_soin"].dt.dayofweek

# E. Est-ce un week-end ?
df["est_weekend"] = df["jour_semaine_soin"].isin([5, 6]).astype(int)

# F. Heure du soin (extraire l'heure)
df["heure_soin_num"] = pd.to_datetime(df["heure_soin"], format="%H:%M", errors="coerce").dt.hour

# G. Montant moyen par ligne
df["montant_moyen_ligne"] = df["montant_total"] / df["nb_lignes"].replace(0, np.nan)

print("Features de base créées.")

# ==============================================
# 3. Aperçu des nouvelles colonnes
# ==============================================
nouvelles_cols = [
    "a_ordonnance", "delai_soin_facture", "delai_facture_reception",
    "jour_semaine_soin", "est_weekend", "heure_soin_num", "montant_moyen_ligne"
]

print("\nAperçu des nouvelles features :")
print(df[nouvelles_cols].describe())

print("\nValeurs manquantes sur les nouvelles features :")
print(df[nouvelles_cols].isnull().sum())

# ==============================================
# 4. Sauvegarde
# ==============================================
output_path = "/data/processed/factures_features_v1.csv"
df.to_csv(output_path, index=False)
print(f"\nFichier sauvegardé : {output_path}")
print("Feature Engineering v1 terminé avec succès.")