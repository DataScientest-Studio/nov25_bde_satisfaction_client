# File: src\api\main.py

"""
Module principal de l'application FastAPI.

Initialise l'application FastAPI, configure les métadonnées
et expose les métriques Prometheus.
"""

from fastapi import FastAPI, Request
from api.routes import predict
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from prometheus_client import Counter
from api.routes.stats import router as stats_router



# Création de l’application FastAPI
app = FastAPI(
    title="API de prédiction de sentiment des avis clients",
    description=(
        "Cette API permet de prédire le sentiment des avis clients "
        "en utilisant un modèle de traitement du langage naturel."
    ),
    version="1.0.0",
)
app.include_router(stats_router)


# Compteur
API_REQUESTS_TOTAL = Counter(
    name="api_requests_total",
    documentation="Nombre total de requêtes traitées par l'API",
    labelnames=["method", "route", "status"]
)

# Instrumentation Prometheus automatique (HTTP, latence, status)
PrometheusFastApiInstrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True
).instrument(app).expose(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware pour incrémenter un compteur Prometheus métier.
    """
    response = await call_next(request)

    route = request.scope.get("route")
    route_path = route.path if route else "unknown"

    API_REQUESTS_TOTAL.labels(
        method=request.method,
        route=route_path,
        status=response.status_code
    ).inc()

    return response


# Inclusion des routes API
app.include_router(predict.router)
