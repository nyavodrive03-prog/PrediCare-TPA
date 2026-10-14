import joblib
import pandas as pd
import shap

print("Test SHAP")

model = joblib.load("/ml/models/fraud_model_xgb.pkl")
feature_names = joblib.load("/ml/models/feature_names.pkl")

df = pd.read_csv("/data/processed/dataset_final_fraude.csv")
X = df[feature_names].head(5)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

print("SHAP calculé avec succès sur 5 exemples.")
print("Forme des SHAP values :", shap_values.shape)