import pandas as pd
import numpy as np

print("Préparation du dataset final pour le modèle de fraude")

# Charger la dernière version
df = pd.read_csv("/data/processed/factures_features_v3.csv")
print(f"Données chargées : {df.shape}")

# ==============================================
# 1. Sélection des colonnes utiles
# ==============================================

# Colonnes à garder (features + cible)
colonnes_utiles = [
    # Identifiants (on les garde temporairement)
    "facture_id",
    
    # Cible
    "est_fraude",
    
    # Features numériques de base
    "nb_lignes", "montant_total", "montant_eligible", "reste_a_charge",
    "a_ordonnance", "delai_soin_facture", "delai_facture_reception",
    "jour_semaine_soin", "est_weekend", "heure_soin_num", "montant_moyen_ligne",
    
    # Features lignes
    "nb_lignes_reel", "quantite_totale", "quantite_max",
    "prix_unitaire_max", "prix_unitaire_moyen", "montant_lignes_total",
    "nb_actes", "nb_medicaments", "diff_nb_lignes", "ratio_medicaments",
    
    # Features tarif
    "ecart_tarif_moyen", "ecart_tarif_max", "ecart_tarif_pct_moyen",
    "nb_lignes_surfacturees", "nb_lignes_avec_tarif",
    
    # Prestataires
    "type_prestataire", "niveau_tarif", "note_qualite", "conventionne",
    
    # Type de facture (utile)
    "type_facture", "canal_reception", "mode_reglement"
]

# Garder uniquement les colonnes qui existent
colonnes_existantes = [col for col in colonnes_utiles if col in df.columns]
df = df[colonnes_existantes].copy()

print(f"Colonnes sélectionnées : {len(colonnes_existantes)}")

# ==============================================
# 2. Encodage simple des variables catégorielles
# ==============================================

# type_prestataire
df["type_prestataire"] = df["type_prestataire"].fillna("INCONNU")
df = pd.get_dummies(df, columns=["type_prestataire"], prefix="type_prest")

# niveau_tarif
df["niveau_tarif"] = df["niveau_tarif"].fillna("INCONNU")
df = pd.get_dummies(df, columns=["niveau_tarif"], prefix="niveau")

# type_facture
df["type_facture"] = df["type_facture"].fillna("INCONNU")
df = pd.get_dummies(df, columns=["type_facture"], prefix="type_fac")

# canal_reception
df["canal_reception"] = df["canal_reception"].fillna("INCONNU")
df = pd.get_dummies(df, columns=["canal_reception"], prefix="canal")

# mode_reglement
df["mode_reglement"] = df["mode_reglement"].fillna("INCONNU")
df = pd.get_dummies(df, columns=["mode_reglement"], prefix="mode")

print(f"Après encodage : {df.shape}")

# ==============================================
# 3. Vérifications finales
# ==============================================

print("\nRépartition de la cible :")
print(df["est_fraude"].value_counts())
print(f"Taux de fraude : {df['est_fraude'].mean()*100:.2f}%")

print("\nValeurs manquantes restantes :")
missing = df.isnull().sum()
missing = missing[missing > 0]
if len(missing) > 0:
    print(missing)
else:
    print("Aucune valeur manquante")

# ==============================================
# 4. Sauvegarde du dataset final
# ==============================================
output_path = "/data/processed/dataset_final_fraude.csv"
df.to_csv(output_path, index=False)
print(f"\nDataset final sauvegardé : {output_path}")
print("Préparation terminée avec succès.")