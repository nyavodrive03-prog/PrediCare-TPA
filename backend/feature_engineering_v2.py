import pandas as pd
import numpy as np

print("Feature Engineering v2 - Agrégation des lignes de facture")

# Charger les données
df = pd.read_csv("/data/processed/factures_features_v1.csv")
lignes = pd.read_csv("/data/raw/dataset/lignes_facture.csv")

print(f"Factures : {df.shape}")
print(f"Lignes   : {lignes.shape}")

# ==============================================
# 1. Statistiques par facture à partir des lignes
# ==============================================

agg_lignes = lignes.groupby("facture_id").agg(
    nb_lignes_reel = ("ligne_id", "count"),
    quantite_totale = ("quantite", "sum"),
    quantite_max = ("quantite", "max"),
    prix_unitaire_max = ("prix_unitaire", "max"),
    prix_unitaire_moyen = ("prix_unitaire", "mean"),
    montant_lignes_total = ("montant", "sum"),
    nb_actes = ("type_ligne", lambda x: (x == "ACTE").sum()),
    nb_medicaments = ("type_ligne", lambda x: (x == "MEDICAMENT").sum())
).reset_index()

print("Agrégations créées.")

# ==============================================
# 2. Fusion avec le dataframe principal
# ==============================================

df = df.merge(agg_lignes, on="facture_id", how="left")

# Remplir les éventuels manquants (au cas où)
df["nb_lignes_reel"] = df["nb_lignes_reel"].fillna(0).astype(int)
df["quantite_totale"] = df["quantite_totale"].fillna(0)
df["quantite_max"] = df["quantite_max"].fillna(0)
df["prix_unitaire_max"] = df["prix_unitaire_max"].fillna(0)
df["prix_unitaire_moyen"] = df["prix_unitaire_moyen"].fillna(0)
df["montant_lignes_total"] = df["montant_lignes_total"].fillna(0)
df["nb_actes"] = df["nb_actes"].fillna(0).astype(int)
df["nb_medicaments"] = df["nb_medicaments"].fillna(0).astype(int)

print(f"Après fusion : {df.shape}")

# ==============================================
# 3. Features supplémentaires
# ==============================================

# Différence entre nb_lignes déclaré et réel
df["diff_nb_lignes"] = df["nb_lignes"] - df["nb_lignes_reel"]

# Ratio médicaments / actes
df["ratio_medicaments"] = df["nb_medicaments"] / (df["nb_lignes_reel"] + 1)

print("Features supplémentaires créées.")

# ==============================================
# 4. Aperçu
# ==============================================
nouvelles = [
    "nb_lignes_reel", "quantite_totale", "quantite_max",
    "prix_unitaire_max", "prix_unitaire_moyen", "montant_lignes_total",
    "nb_actes", "nb_medicaments", "diff_nb_lignes", "ratio_medicaments"
]

print("\nAperçu des nouvelles features :")
print(df[nouvelles].describe())

print("\nValeurs manquantes :")
print(df[nouvelles].isnull().sum())

# ==============================================
# 5. Sauvegarde
# ==============================================
output_path = "/data/processed/factures_features_v2.csv"
df.to_csv(output_path, index=False)
print(f"\nFichier sauvegardé : {output_path}")
print("Feature Engineering v2 terminé avec succès.")