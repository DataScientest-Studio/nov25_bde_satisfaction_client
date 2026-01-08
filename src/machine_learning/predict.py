# File: src\machine_learning\predict.py

"""
Module pour la prédiction du sentiment d'avis utilisateurs.
"""

from typing import Dict
from transformers import pipeline, logging
from etl.utils.data_utils import DataUtils


# Désactive les messages info de Transformers
logging.set_verbosity_error()

# Chargement du modèle de sentiment via pipeline
# (en dehors de la fonction pour éviter de le recharger à chaque appel dans fastAPI par exemple)
_model = pipeline(
    task="sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    truncation=True,
)


def convert_stars_to_sentiment(label: str) -> str:
    """
    Convertit une prédiction du modèle exprimée en étoiles
    (1 à 5 étoiles) en un sentiment textuel simplifié.

    Les correspondances sont les suivantes :
    - 1 ou 2 étoiles => Négatif
    - 3 étoiles      => Neutre
    - 4 ou 5 étoiles => Positif

    Cette fonction permet de normaliser la sortie du modèle
    de sentiment en trois catégories exploitables.

    Parameters
    ----------
    label : str
        Label retourné par le modèle Hugging Face
        ("1 star", "3 stars", "5 stars").

    Returns
    -------
    str
        Sentiment normalisé : "Négatif", "Neutre" ou "Positif".

    Raises
    ------
    ValueError
        Si le label fourni ne correspond pas à une valeur attendue.

    """
    label = label.upper()

    if label in ["1 STAR", "2 STARS"]:
        return "Négatif"
    elif label == "3 STARS":
        return "Neutre"
    elif label in ["4 STARS", "5 STARS"]:
        return "Positif"
    else:
        raise ValueError(f"Label inattendu : {label}")


def predict_sentiment(text: str) -> Dict[str, str]:
    """
    Prédit le sentiment d'un avis utilisateur à partir d'un modèle
    de traitement du langage naturel (NLP).

    Le modèle utilisé est :
    - cmarkea/distilcamembert-base-sentiment (Hugging Face)

    Le modèle est entrainé à prédire une note de 1 à 5 étoiles à partir d'un texte.
    Ensuite, dans le code y a une étape de normalisation qui convertit ces
    notes en trois catégories de sentiment :
    - Négatif (1-2 étoiles)
    - Neutre  (3 étoiles)
    - Positif (4-5 étoiles)

    Lors de la première exécution en local sur la machine, les fichiers du modèle
    et du tokenizer sont téléchargés et stockés dans le cache local de Hugging Face
    sur le disque. Lors des exécutions suivantes du script, ces fichiers sont
    automatiquement réutilisés depuis le cache local et ne sont pas
    retéléchargés.

    Parameters
    ----------
    text : str
        Texte brut correspondant à un avis utilisateur.

    Returns
    -------
    Dict[str, str]
        Dictionnaire contenant :
        - text_clean : texte nettoyé utilisé pour la prédiction
        - sentiment  : sentiment prédit (POSITIVE, NEUTRAL ou NEGATIVE)

    Raises
    ------
    ValueError
        Si le texte fourni est vide ou invalide après nettoyage.
    """

    text_clean = DataUtils.clean_text(text)

    if not text_clean:
        raise ValueError("L'avis fourni est vide ou non valide.")

    # Prédiction du sentiment
    result = _model(text_clean, max_length=512)[0]
    sentiment = convert_stars_to_sentiment(result["label"])

    return {
        "text_clean": text_clean,
        "sentiment": sentiment
    }
