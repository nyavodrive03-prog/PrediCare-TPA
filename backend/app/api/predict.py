from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import httpx

from app.db.database import get_db
from app.db.models import Prediction
from app.services.prediction import predict_fraud

router = APIRouter(prefix="/predict", tags=["Prédiction Fraude"])

# URL de ton webhook n8n
N8N_WEBHOOK_URL = "http://n8n:5678/webhook/fraude-alerte"

class FactureInput(BaseModel):
    data: Dict[str, Any]
    facture_id: Optional[str] = None

@router.post("/")
def predict(facture: FactureInput, db: Session = Depends(get_db)):
    try:
        # 1. Faire la prédiction
        result = predict_fraud(facture.data)

        # 2. Sauvegarder en base
        prediction_db = Prediction(
            facture_id=facture.facture_id,
            score_fraude=result["score_fraude"],
            prediction=result["prediction"],
            explication=json.dumps(result["explication"], ensure_ascii=False)
        )
        db.add(prediction_db)
        db.commit()
        db.refresh(prediction_db)

        result["prediction_id"] = prediction_db.id

        # 3. Envoyer une alerte à n8n si le score est élevé
        if result["score_fraude"] > 0.8:
            try:
                # On envoie les infos à n8n
                payload = {
                    "score_fraude": result["score_fraude"],
                    "prediction": result["prediction"],
                    "facture_id": facture.facture_id,
                    "explication": result["explication"]
                }
                httpx.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
                result["alerte_envoyee"] = True
            except Exception as e:
                result["alerte_envoyee"] = False
                result["alerte_erreur"] = str(e)
        else:
            result["alerte_envoyee"] = False

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))