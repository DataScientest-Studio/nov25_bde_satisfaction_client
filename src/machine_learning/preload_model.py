# File: src\machine_learning\preload_model.py

"""
Module pour pré-charger le modèle Hugging Face pour le Dockerfile_api
"""

from transformers import pipeline, logging

# Désactiver les warnings inutiles
logging.set_verbosity_error()

print("Téléchargement du modèle de sentiment...")

# Charger le modèle et le tokenizer (Hugging Face)
pipeline(
    task="sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    truncation=True,
)

print("Modèle téléchargé avec succès !")
