from pydantic import BaseModel

# Modèles de schéma pour les requêtes et réponses de l'API


class PredictResponse(BaseModel):
    text_clean: str
    sentiment: str


class PredictRequest(BaseModel):
    text: str
