# File: src\etl\load\elasticsearch_bulk_loader.py

"""
Module pour le mapping Elasticsearch pour les avis clients.

Ce module expose le dictionnaire `MAPPING_REVIEWS`, utilisé pour créer
ou valider l'index Elasticsearch lors de la phase de chargement (Load)
du pipeline ETL.

Tous les champs sont typés explicitement et le mode `dynamic: strict`
empêche l'indexation de champs non déclarés.
"""

# Dictionnaire pour typer mes attributs
MAPPING_REVIEWS = {
    "dynamic": "strict",
    "properties": {
        "id_review": {"type": "keyword"},
        "is_verified": {"type": "boolean"},

        # Dates métier
        "date_review": {"type": "date"},
        "date_response": {"type": "date"},

        # Timestamps techniques
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},

        "id_user": {"type": "keyword"},
        "user_name": {
            "type": "text",
            "fields": {"raw": {"type": "keyword"}}
        },
        "user_review": {"type": "text"},
        "user_review_length": {"type": "integer"},
        "user_rating": {"type": "float"},

        "enterprise_name": {
            "type": "text",
            "fields": {"raw": {"type": "keyword"}}
        },
        "enterprise_response": {"type": "text"},
        "enterprise_url": {"type": "keyword"},
        "enterprise_rating": {"type": "float"},
        "enterprise_review_number": {"type": "integer"},
        "enterprise_percentage_one_star": {"type": "integer"},
        "enterprise_percentage_two_star": {"type": "integer"},
        "enterprise_percentage_three_star": {"type": "integer"},
        "enterprise_percentage_four_star": {"type": "integer"},
        "enterprise_percentage_five_star": {"type": "integer"},
    },
}
