import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, recall_score, precision_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import joblib
import os

print("Entraînement du modèle de fraude - XGBoost")

# 1. Charger le dataset final
df = pd.read_csv("/data/processed/dataset_final_fraude.csv")
print(f"Dataset chargé : {df.shape}")

# 2. Séparer X et y
y = df["est_fraude"]
X = df.drop(columns=["est_fraude", "facture_id"], errors="ignore")

# Garder uniquement les colonnes numériques
X = X.select_dtypes(include=[np.number])
print(f"Features utilisées : {X.shape[1]}")

# 3. Train / Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train : {X_train.shape} | Test : {X_test.shape}")
print(f"Taux de fraude train : {y_train.mean()*100:.2f}%")

# 4. SMOTE (pour gérer le déséquilibre)
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print(f"Après SMOTE : {X_train_res.shape}")
print(f"Taux de fraude après SMOTE : {y_train_res.mean()*100:.2f}%")

# 5. Entraînement XGBoost (focus Recall)
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=1,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_res, y_train_res)

# 6. Évaluation
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n=== RAPPORT DE CLASSIFICATION ===")
print(classification_report(y_test, y_pred))

print(f"Recall     : {recall_score(y_test, y_pred):.4f}")
print(f"Precision  : {precision_score(y_test, y_pred):.4f}")
print(f"F1-Score   : {f1_score(y_test, y_pred):.4f}")
print(f"ROC-AUC    : {roc_auc_score(y_test, y_proba):.4f}")

# 7. Sauvegarde du modèle
os.makedirs("/ml/models", exist_ok=True)
model_path = "/ml/models/v1/fraud_model_xgb.pkl"
joblib.dump(model, model_path)
print(f"\nModèle sauvegardé : {model_path}")

# Sauvegarder aussi les noms des colonnes
joblib.dump(list(X.columns), "/ml/models/v1/feature_names.pkl")
print("Noms des features sauvegardés.")

print("\nEntraînement terminé avec succès.")