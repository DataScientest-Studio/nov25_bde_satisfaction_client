from fastapi import APIRouter
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
    response_model=PredictResponse
)
# ajout de la fonction de gestion de la route
def predict(request: PredictRequest) -> PredictResponse:
    return predict_sentiment(request.text)

