# File: tests\test_predict.py

"""
Ce module contient des tests unitaires pour les fonctions de prédiction de sentiment
et de conversion d'étoiles en sentiment. Il inclut des tests pour la fonction 
convert_stars_to_sentiment et la fonction predict_sentiment avec un mock du nettoyage 
de texte et du modèle de prédiction.
"""

import pytest
from unittest import mock
from machine_learning.predict import predict_sentiment, convert_stars_to_sentiment
from etl.utils.data_utils import DataUtils


# Test pour la fonction convert_stars_to_sentiment
def test_convert_stars_to_sentiment():
    # Test pour chaque label possible
    assert convert_stars_to_sentiment("1 star") == "NÉGATIF"
    assert convert_stars_to_sentiment("2 stars") == "NÉGATIF"
    assert convert_stars_to_sentiment("3 stars") == "NEUTRE"
    assert convert_stars_to_sentiment("4 stars") == "POSITIF"
    assert convert_stars_to_sentiment("5 stars") == "POSITIF"
    
    # Test d'un label inattendu
    with pytest.raises(ValueError):
        convert_stars_to_sentiment("6 stars")

# Test unitaire pour la fonction 'predict_sentiment' avec un mock
def test_predict_sentiment():
    # Mock du clean_text directement dans le test
    with mock.patch.object(DataUtils, 'clean_text', return_value="This is a clean review.") as mock_clean_text, \
         mock.patch('machine_learning.predict._model', return_value=[{'label': '5 stars'}]):

        result = predict_sentiment("This is a great product!")
    
    # Vérifier que la fonction retourne bien le sentiment attendu
    assert result["sentiment"] == "POSITIF"
    
    # Vérifier que le texte nettoyé est bien celui attendu
    assert result["text_clean"] == "This is a clean review."
