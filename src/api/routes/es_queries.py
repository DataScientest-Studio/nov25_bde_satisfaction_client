# File: src\api\routes\es_queries.py

"""
Module FastAPI pour exécuter des requêtes Elasticsearch sur l'index `reviews`.
"""

from fastapi import APIRouter
from elasticsearch import Elasticsearch

router = APIRouter(tags=["Elasticsearch Queries"])

# Connexion à Elasticsearch (le container Docker)
ELASTICSEARCH_URL = "http://es-satisfaction:9200"
es = Elasticsearch(ELASTICSEARCH_URL)

INDEX_NAME = "reviews"


@router.get(
    "/stats",
    summary="Statistiques des avis",
    description="Retourne des statistiques simples sur les avis clients stockés dans Elasticsearch, "
                "comme la note moyenne et la distribution des notes.",
    response_description="Statistiques sur les avis",
)
def get_review_stats():
    """Statistiques simples sur les reviews."""
    response = es.search(index=INDEX_NAME, size=200, query={"match_all": {}})
    hits = response["hits"]["hits"]
    total = len(hits)

    if total == 0:
        return {"total_reviews": 0}

    ratings = [
        float(h["_source"].get("user_rating") or h["_source"].get("enterprise_rating"))
        for h in hits
        if h["_source"].get("user_rating") or h["_source"].get("enterprise_rating")
    ]

    avg_rating = sum(ratings) / len(ratings) if ratings else None

    distribution = {}
    for r in ratings:
        distribution[r] = distribution.get(r, 0) + 1

    return {
        "total_reviews": total,
        "average_rating": avg_rating,
        "rating_distribution": distribution,
    }


@router.get(
    "/mapping",
    summary="Mapping de l'index",
    description="Récupère le mapping de l'index `reviews` dans Elasticsearch.",
    response_description="Structure des champs de l'index",
)
def get_index_mapping():
    """Récupère le mapping de l'index `reviews`."""
    return es.indices.get_mapping(index=INDEX_NAME)


@router.get(
    "/count",
    summary="Nombre de documents",
    description="Compte le nombre total de documents présents dans l'index `reviews`.",
    response_description="Nombre de documents",
)
def count_documents():
    """Compte le nombre de documents dans l'index `reviews`."""
    return es.count(index=INDEX_NAME)


@router.get(
    "/latest",
    summary="Dernières reviews",
    description="Récupère les dernières reviews les plus récentes, triées par identifiant décroissant.",
    response_description="Liste des dernières reviews",
)
def get_latest_reviews(size: int = 15):
    """Récupère les dernières reviews les plus récentes."""
    query = {
        "size": size,
        "sort": [{"id_review": {"order": "desc"}}]
    }
    response = es.search(index=INDEX_NAME, body=query)
    hits = response["hits"]["hits"]
    return [h["_source"] for h in hits]
