from fastapi import FastAPI
from src.api.routes import predict

# Création de l’application FastAPI
app = FastAPI(
    title="API de prédiction de sentiment des avis clients",
    description="Cette API permet de prédire le sentiment des avis clients en utilisant un modèle de traitement du langage naturel.",
    version="1.0.0",
)

# Inclusion des routes
app.include_router(predict.router)
