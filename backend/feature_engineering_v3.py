import pandas as pd
import numpy as np

print("Feature Engineering v3 - Tarifs + Prestataires (version corrigée)")

# Charger les données
df = pd.read_csv("/data/processed/factures_features_v2.csv")
lignes = pd.read_csv("/data/raw/dataset/lignes_facture.csv")
grille = pd.read_csv("/data/raw/dataset/grille_tarifaire.csv")
prestataires = pd.read_csv("/data/raw/dataset/prestataires.csv")

print(f"Factures     : {df.shape}")
print(f"Lignes       : {lignes.shape}")
print(f"Grille       : {grille.shape}")
print(f"Prestataires : {prestataires.shape}")

# ==============================================
# 1. Ajouter prestataire_id aux lignes
# ==============================================

# On récupère prestataire_id depuis les factures
factures_simple = df[["facture_id", "prestataire_id"]].drop_duplicates()

lignes = lignes.merge(factures_simple, on="facture_id", how="left")

print("prestataire_id ajouté aux lignes.")

# ==============================================
# 2. Calculer l'écart de tarif (surfacturation)
# ==============================================

lignes_tarif = lignes.merge(
    grille,
    on=["prestataire_id", "code"],
    how="left"
)

# Calculer l'écart de prix
lignes_tarif["ecart_tarif"] = lignes_tarif["prix_unitaire"] - lignes_tarif["tarif_pratique"]
lignes_tarif["ecart_tarif_pct"] = (lignes_tarif["ecart_tarif"] / lignes_tarif["tarif_pratique"].replace(0, np.nan)) * 100

# Agréger par facture
agg_tarif = lignes_tarif.groupby("facture_id").agg(
    ecart_tarif_moyen = ("ecart_tarif", "mean"),
    ecart_tarif_max = ("ecart_tarif", "max"),
    ecart_tarif_pct_moyen = ("ecart_tarif_pct", "mean"),
    nb_lignes_surfacturees = ("ecart_tarif", lambda x: (x > 0).sum()),
    nb_lignes_avec_tarif = ("tarif_pratique", lambda x: x.notna().sum())
).reset_index()

print("Features de tarif créées.")

# ==============================================
# 3. Informations prestataires
# ==============================================

prestataires_clean = prestataires[[
    "prestataire_id", "type_prestataire", "niveau_tarif",
    "note_qualite", "conventionne", "ville"
]].copy()

# ==============================================
# 4. Fusion finale
# ==============================================

df = df.merge(agg_tarif, on="facture_id", how="left")
df = df.merge(prestataires_clean, on="prestataire_id", how="left")

# Remplir les manquants
for col in ["ecart_tarif_moyen", "ecart_tarif_max", "ecart_tarif_pct_moyen",
            "nb_lignes_surfacturees", "nb_lignes_avec_tarif"]:
    df[col] = df[col].fillna(0)

print(f"Après fusion : {df.shape}")

# ==============================================
# 5. Aperçu
# ==============================================
print("\nAperçu des nouvelles features numériques :")
print(df[["ecart_tarif_moyen", "ecart_tarif_max", "ecart_tarif_pct_moyen",
          "nb_lignes_surfacturees", "nb_lignes_avec_tarif"]].describe())

print("\nRépartition type_prestataire :")
print(df["type_prestataire"].value_counts(dropna=False).head(10))

print("\nValeurs manquantes sur les nouvelles colonnes :")
nouvelles = [
    "ecart_tarif_moyen", "ecart_tarif_max", "ecart_tarif_pct_moyen",
    "nb_lignes_surfacturees", "nb_lignes_avec_tarif",
    "type_prestataire", "niveau_tarif", "note_qualite", "conventionne"
]
print(df[nouvelles].isnull().sum())

# ==============================================
# 6. Sauvegarde
# ==============================================
output_path = "/data/processed/factures_features_v3.csv"
df.to_csv(output_path, index=False)
print(f"\nFichier sauvegardé : {output_path}")
print("Feature Engineering v3 terminé avec succès.")