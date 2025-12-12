# File: utils/data_utils.py

"""
Module Utilitaires pour nettoyer, convertir et formater des données.

Ce module contient des fonctions utilitaires pour la manipulation de données textuelles et numériques, ainsi que
des méthodes de formatage de dates. Les méthodes sont principalement utilisées pour nettoyer, convertir et 
normaliser les données dans un format uniforme, en particulier pour les besoins de traitement de données liées 
aux avis des utilisateurs.
"""

import re
import unicodedata
from typing import Any, Optional
from datetime import datetime


class DataUtils:
    """Classe utilitaire pour nettoyer, convertir et formater des données."""

    @staticmethod
    def clean_text(text: Optional[str], max_length: int = 5000) -> Optional[str]:
        """
        Nettoie un texte : supprime les espaces superflus, normalise les caractères Unicode et tronque à une longueur maximale.

        Cette méthode prend en entrée un texte brut, supprime les espaces en excès, normalise les caractères Unicode
        pour uniformiser les caractères spéciaux, puis tronque le texte si sa longueur dépasse la valeur spécifiée.

        Paramètres:
        -----------
        text : str, optionnel
            Le texte à nettoyer. Si 'None' ou une chaîne vide est passé, la méthode retourne 'None'.
        
        max_length : int, optionnel
            La longueur maximale du texte après nettoyage. Par défaut, elle est de 5000 caractères.

        Retourne:
        --------
        str, optionnel
            Le texte nettoyé et tronqué, ou 'None' si le texte d'origine est vide ou non valide (par exemple, si aucun 
            caractère alphanumérique n'est trouvé).
        
        Lève:
        -----
        Exception
            Si un texte non valide est fourni, comme une chaîne qui ne contient pas de caractères alphanumériques, 
            la méthode retourne 'None'.
        """
        if not text:
            return None
        # Normalise les caractères Unicode pour uniformiser le texte
        text = unicodedata.normalize("NFKC", text)
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        if not re.search(r'[a-zA-Z0-9]', text):
            return None
        return text[:max_length]

    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """
        Convertit une valeur en float, renvoie la valeur par défaut si la conversion échoue.

        Cette méthode tente de convertir la valeur d'entrée en float. Si la conversion échoue, elle renvoie la valeur 
        par défaut spécifiée.

        Paramètres:
        -----------
        value : Any
            La valeur à convertir en float. Elle peut être de tout type (str, int, etc.).
        
        default : float, optionnel
            La valeur retournée si la conversion échoue. Par défaut, elle est de '0.0'.

        Retourne:
        --------
        float
            La valeur convertie en float, ou la valeur par défaut si la conversion échoue.

        Lève:
        -----
        Exception
            Si la valeur ne peut pas être convertie en float et que la conversion échoue, la valeur par défaut est
            renvoyée.
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """
        Convertit une valeur en int, renvoie la valeur par défaut si la conversion échoue.

        Cette méthode tente de convertir la valeur d'entrée en entier (int). Si la conversion échoue, elle renvoie la 
        valeur par défaut spécifiée.

        Paramètres:
        -----------
        value : Any
            La valeur à convertir en entier (int). Elle peut être de tout type (str, float, etc.).
        
        default : int, optionnel
            La valeur retournée si la conversion échoue. Par défaut, elle est de '0'.

        Retourne:
        --------
        int
            La valeur convertie en entier, ou la valeur par défaut si la conversion échoue.

        Lève:
        -----
        Exception
            Si la valeur ne peut pas être convertie en int et que la conversion échoue, la valeur par défaut est
            renvoyée.
        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def format_date(date_str: Optional[str]) -> Optional[str]:
        """
        Convertit une chaîne de date ISO en format 'YYYY-MM-DD', renvoie 'None' si la date est invalide.

        Cette méthode prend en entrée une chaîne de caractères représentant une date au format ISO 8601 (par exemple,
        '2023-12-12T14:25:00Z'), et la convertit en une chaîne de format 'YYYY-MM-DD'. Si la date est invalide ou 
        mal formatée, la méthode retourne 'None'.

        Paramètres:
        -----------
        date_str : str, optionnel
            La chaîne de caractères représentant la date à convertir. Si 'None' est passé, la méthode retourne 'None'.

        Retourne:
        --------
        str, optionnel
            La date formatée en 'YYYY-MM-DD', ou 'None' si la chaîne de date est invalide.

        Lève:
        -----
        Exception
            Si la date est mal formatée et qu'elle ne peut pas être convertie, la méthode retourne 'None'.
        """
        if date_str:
            try:
                # Convertit une date ISO 8601 en format YYYY-MM-DD, en gérant le suffixe 'Z' pour UTC
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date().isoformat()
            except Exception:
                return None
        return None
