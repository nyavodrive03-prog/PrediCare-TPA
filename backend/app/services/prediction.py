import joblib
import pandas as pd
import numpy as np
import shap
from typing import Dict, Any
from pathlib import Path

MODEL_PATH = Path("/ml/models/v1/fraud_model_xgb.pkl")
FEATURES_PATH = Path("/ml/models/v1/feature_names.pkl")

print("Chargement du modèle de fraude...")

model = None
feature_names = None
explainer = None

try:
    if MODEL_PATH.exists() and FEATURES_PATH.exists():
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURES_PATH)
        explainer = shap.TreeExplainer(model)
        print("Modèle et SHAP chargés avec succès.")
    else:
        print("Attention : fichiers du modèle introuvables. Mode test / CI.")
except Exception as e:
    print(f"Erreur lors du chargement du modèle : {e}")

def predict_fraud(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Créer un DataFrame
        df = pd.DataFrame([data])

        # Ajouter les colonnes manquantes avec 0
        for col in feature_names:
            if col not in df.columns:
                df[col] = 0

        # Garder uniquement les features du modèle (dans le bon ordre)
        X = df[feature_names].fillna(0)

        # Prédiction
        proba = float(model.predict_proba(X)[0][1])
        prediction = int(proba >= 0.5)

        # SHAP
        shap_values = explainer.shap_values(X)[0]

        # Top 5 features
        shap_importance = sorted(
            zip(feature_names, shap_values),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        top_features = [
            {
                "feature": str(name),
                "impact": round(float(value), 4),
                "direction": "augmente le risque" if value > 0 else "diminue le risque"
            }
            for name, value in shap_importance
        ]

        return {
            "score_fraude": round(proba, 4),
            "prediction": prediction,
            "est_fraude": bool(prediction),
            "seuil_utilise": 0.5,
            "explication": top_features
        }

    except Exception as e:
        raise Exception(f"Erreur lors de la prédiction : {str(e)}")