# File: src/api/routes/stats.py

from fastapi import APIRouter
from elasticsearch import Elasticsearch

router = APIRouter(tags=["Stats"])

# Connexion à Elasticsearch (le container Docker)
es = Elasticsearch("http://es-satisfaction:9200")

INDEX_NAME = "reviews"

@router.get("/stats")
def get_review_stats():
    """
    Retourne des statistiques simples sur les reviews Elasticsearch.
    """

    # Récupérer tous les documents (size=200)
    response = es.search(index=INDEX_NAME, size=200, query={"match_all": {}})

    hits = response["hits"]["hits"]
    total = len(hits)

    # Si pas de documents
    if total == 0:
        return {"total_reviews": 0}

    # Extraire les ratings
    ratings = []
    for h in hits:
        source = h["_source"]
        rating = source.get("user_rating") or source.get("enterprise_rating")
        if rating is not None:
            ratings.append(float(rating))

    # Statistiques basiques
    avg_rating = sum(ratings) / len(ratings) if ratings else None

    # Distribution
    distribution = {}
    for r in ratings:
        distribution[r] = distribution.get(r, 0) + 1

    return {
        "total_reviews": total,
        "average_rating": avg_rating,
        "rating_distribution": distribution,
    }
