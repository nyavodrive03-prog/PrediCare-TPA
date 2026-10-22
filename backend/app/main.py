from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base, SessionLocal
from app.db import models
from app.api import auth, predict
import os
from sqlalchemy import text

app = FastAPI(title="PrediCare TPA API", description="API de détection de fraude médicale", version="0.1.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Création des tables
if os.getenv("TESTING") != "1" and os.getenv("CI") != "true":
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Attention : impossible de créer les tables : {e}")

app.include_router(auth.router)
app.include_router(predict.router)

@app.get("/")
def root():
    return {"message": "PrediCare TPA API is running"}

@app.get("/health")
def health_check():
    status = {
        "status": "healthy",
        "service": "predicare-backend",
        "version": "0.1.0",
        "database": "unknown",
        "model_loaded": False
    }

    # Vérifier la base de données
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["database"] = "ok"
    except Exception:
        status["database"] = "error"
        status["status"] = "degraded"

    # Vérifier le modèle (on utilise TON chemin : /ml/models/)
    if os.path.exists("/ml/models/fraud_model_xgb.pkl"):
        status["model_loaded"] = True
    else:
        status["status"] = "degraded"

    return status