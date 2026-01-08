# File: src\tests\test_transform_reviews.py

"""
Test de la transformation des avis pour Elasticsearch avec prise en compte du sentiment utilisateur.

Ce test vérifie que les avis bruts sont correctement transformés en un format compatible 
avec Elasticsearch, en s'assurant que les valeurs par défaut sont appliquées, que les
pourcentages de chaque note sont calculés correctement, et que le champ user_sentiment
est bien généré via le modèle ML (mocké ici pour le test).
"""

from unittest.mock import patch
from etl.transform.transform_reviews import transform_reviews_for_elasticsearch

# Exemple de données brutes
raw_reviews = [
    {
        "reviews": [
            {
                "id": "review_1",
                "consumer": {"id": "user_1"},
                "text": "Great product!",
                "rating": 5,
                "dates": {"publishedDate": "2023-01-01"},
                "reply": {"message": "Thank you!"},
                "labels": {"verification": {"isVerified": True}}
            },
            {
                "id": "review_2",
                "consumer": {"id": "user_2"},
                "text": "",
                "rating": 1,
                "dates": {"publishedDate": "2023-02-01"},
                "reply": None,
                "labels": {"verification": {"isVerified": False}}
            }
        ],
        "enterprise_url": "example-enterprise",
        "enterprise": {
            "name": "Example Enterprise",
            "ratings": {
                "total": 10,
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 2,
                "five": 2
            },
            "enterprise_rating": 4.5,
            "enterprise_review_number": 10
        }
    }
]

# Mock du modèle de sentiment pour rendre le test déterministe
@patch("etl.transform.transform_reviews.predict_sentiment")
def test_transform_reviews_for_elasticsearch(mock_predict):
    # On force le modèle à renvoyer Neutre pour tous les textes
    mock_predict.side_effect = lambda text: {"text_clean": text, "sentiment": "Neutre"}

    transformed_reviews = transform_reviews_for_elasticsearch(raw_reviews)

    # Vérifier qu'il y a bien deux avis transformés
    assert len(transformed_reviews) == 2

    # Vérifier le premier avis
    first_review = transformed_reviews[0]
    assert first_review["id_review"] == "review_1"
    assert first_review["is_verified"] is True
    assert first_review["user_review"] == "Great product!"
    assert first_review["user_rating"] == 5.0
    assert first_review["enterprise_name"] == "Example Enterprise"
    assert first_review["enterprise_percentage_five_star"] == 20  # 2/10 * 100

    # Vérifier le deuxième avis (vides et non vérifié)
    second_review = transformed_reviews[1]
    assert second_review["id_review"] == "review_2"
    assert second_review["is_verified"] is False
    assert second_review["user_review"] == "indisponible"  # Avis vide
    assert second_review["user_rating"] == 1.0
    assert second_review["enterprise_name"] == "Example Enterprise"
    assert second_review["enterprise_percentage_one_star"] == 10  # 1/10 * 100

    # Vérifier que les valeurs par défaut sont appliquées quand nécessaire
    assert second_review["enterprise_response"] == "indisponible"  # Pas de réponse de l'entreprise
    assert second_review["date_response"] is None  # Pas de réponse de l'entreprise, donc None

    # Vérifier les pourcentages
    assert first_review["enterprise_percentage_one_star"] == 10
    assert first_review["enterprise_percentage_two_star"] == 20
    assert first_review["enterprise_percentage_three_star"] == 30
    assert first_review["enterprise_percentage_four_star"] == 20
    assert first_review["enterprise_percentage_five_star"] == 20

    # Vérifier le champ user_sentiment
    assert first_review["user_sentiment"] == "Neutre"
    assert second_review["user_sentiment"] == "Neutre"
