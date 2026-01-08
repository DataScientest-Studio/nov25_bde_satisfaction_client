# File: src\tests\test_load_reviews_to_elasticsearch_bulk.py

"""
Tests unitaires pour la fonction 'load_reviews_to_elasticsearch_bulk' dans le module
'elasticsearch_bulk_loader'. Vérifie l'insertion et la mise à jour de documents dans 
Elasticsearch via le bulk API.
"""

import pytest
from unittest.mock import patch
from etl.load.elasticsearch_bulk_loader import load_reviews_to_elasticsearch_bulk


@pytest.fixture
def mock_es():
    # Crée un mock de la connexion Elasticsearch
    with patch("etl.load.elasticsearch_bulk_loader.Elasticsearch") as MockEs:
        mock_es_instance = MockEs.return_value
        mock_es_instance.ping.return_value = True  # Simule une connexion réussie
        yield mock_es_instance


@patch("etl.load.elasticsearch_bulk_loader.helpers.bulk")
def test_load_reviews_to_elasticsearch_bulk(mock_bulk, mock_es):
    # Exemple de document à tester
    documents = [
        {"id_review": "123", "review_text": "Super produit!"},
        {"id_review": "124", "review_text": "Moyen, mais correct."},
    ]

    # Simule le comportement de helpers.bulk : elle doit renvoyer un tuple (success, errors)
    mock_bulk.return_value = (2, [])  # 2 documents insérés, aucune erreur

    # Appel de la fonction avec les documents à insérer
    load_reviews_to_elasticsearch_bulk(documents, es_host="http://localhost:9200/", index="reviews")

    # Vérifie que la méthode ping() a été appelée pour vérifier la connexion
    mock_es.ping.assert_called_once()

    # Vérifie que helpers.bulk a bien été appelé avec les actions de mise à jour / insertion
    mock_bulk.assert_called_once()  # Vérifie qu'on a bien appelé helpers.bulk

    # Vérifie que l'action bulk contient bien des documents à insérer
    actions = mock_bulk.call_args[0][1]  # Récupère les arguments passés à helpers.bulk
    assert len(actions) == len(documents)  # Une action par document

    # Vérifie qu'un champ 'updated_at' est présent dans chaque action
    for action in actions:
        assert "updated_at" in action["doc"]
        assert "created_at" in action["upsert"]
