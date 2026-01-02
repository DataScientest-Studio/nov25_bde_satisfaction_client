# File: src\api\schemas.py

"""
Module des schémas pour les requêtes et réponses de l'API
"""

from pydantic import BaseModel


class PredictResponse(BaseModel):
    text_clean: str
    sentiment: str


class PredictRequest(BaseModel):
    text: str
