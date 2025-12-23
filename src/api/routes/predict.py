# File: src\api\routes\predict.py

"""
Module FastAPI pour la prédiction de sentiment des avis clients.

Ce module expose un endpoint permettant d'analyser un texte d'avis client
et de retourner un sentiment (NEGATIF, NEUTRE ou POSITIF) à l'aide
d'un modèle de Machine Learning.
"""

from fastapi import APIRouter, HTTPException
from src.api.schemas import PredictRequest, PredictResponse
from src.machine_learning.predict import predict_sentiment


# Création du routeur pour les endpoints liés à la prédiction
router = APIRouter()

# Endpoint pour prédire le sentiment d'un avis client


@router.post(
    "/predict",
    summary="Prédire le sentiment d'un avis client",
    description="Cette endpoint prend en entrée un texte d'avis client et retourne le sentiment prédit (NEGATIF, NEUTRE, POSITIF).",
    response_description="Le sentiment prédit de l'avis client",
    response_model=PredictResponse,
)
# ajout de la fonction de gestion de la route
def predict(request: PredictRequest) -> PredictResponse:
    """
    Endpoint FastAPI permettant de prédire le sentiment d'un avis client.

    Cette fonction reçoit un texte d'avis client via une requête HTTP,
    appelle le modèle de Machine Learning pour effectuer la prédiction,
    puis retourne le sentiment associé (NEGATIF, NEUTRE ou POSITIF).

    Si le texte fourni est vide ou invalide, une erreur HTTP 400 est levée.

    Parameters
    ----------
    request : PredictRequest
        Objet contenant le texte de l'avis client à analyser.

    Returns
    -------
    PredictResponse
        Objet contenant :
        - text_clean : texte nettoyé utilisé pour la prédiction
        - sentiment  : sentiment prédit (NEGATIF, NEUTRE ou POSITIF)

    Raises
    ------
    HTTPException
        Erreur HTTP 400 si le texte fourni est vide ou non valide.
    """
    try:
        return predict_sentiment(request.text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
