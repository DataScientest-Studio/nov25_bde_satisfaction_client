# File: src\etl\transform\transform_reviews.py

"""
Module pour transformer les avis en documents compatibles Elasticsearch.

Ce module permet de transformer les avis récupérés depuis en documents structurés et prêts à être
indexés dans Elasticsearch. Les avis vides sont remplacés par des valeurs par défaut ("indisponible"), et
les informations sont nettoyées et formatées pour une insertion efficace dans Elasticsearch.
"""

import math
import re
from typing import Dict, Any, List
from etl.utils.data_utils import DataUtils


def anonymize_enterprise_response(text: str) -> str:
    """
    Anonymise un texte en remplaçant les fautes de salutation, prénoms et noms par des valeurs génériques.
    Vérifier à l'aide de https://regex101.com/

    Parameters
    ----------
    text : str
        Texte à anonymiser.

    Returns
    ---------
    str
        Texte anonymisé.
    """
    # 1. Remplacer les fautes courantes par "Bonjour"
    text = re.sub(r"^(Bonour|Bonnour|Bonjouir|Bonsoir)", "Bonjour", text)
    # 2. Remplacer les salutations comme "Bonjour Madame", "Bonjour Monsieur", etc.
    text = re.sub(r"^(Bonjour) (Madame, Monsieur|Madame|Monsieur|Mme|M\.|Mr|Melle|M)? ?([\wÀ-ÿ-]+)(,|$)", "Bonjour,", text)
    # 3. Remplacer "Bonjour" suivi d'un prénom simple (un mot commençant par une majuscule)
    text = re.sub(r"^(Bonjour), ?([A-Za-zÀ-ÿ-]+)(,|$)", "Bonjour,", text)
    # 4. Remplacer "Bonjour" suivi d'un prénom composé
    text = re.sub(r"^(Bonjour) ([A-Za-zÀ-ÿ-]+(?: [A-Za-zÀ-ÿ-]+)*),", "Bonjour,", text)
    # 5. Remplacer "Bonjour" suivi d'un prénom composé (deux mots ou plus) pour ne garder que le dernier prénom
    text = re.sub(r"^(Bonjour), (\s*[A-ZÀ-ÿ][a-zÀ-ÿ]+)(\s+[A-ZÀ-ÿ][a-zÀ-ÿ]+)", lambda m: f"Bonjour, {m.group(3).strip()}", text)
    # 6. Enlever tout prénom ou nom à la fin de la phrase
    text = re.sub(r"\s+[A-Z][a-z]+$", "", text)
    return text

def transform_reviews_for_elasticsearch(raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme tous les avis de toutes les entreprises en documents prêts pour Elasticsearch,
    en nettoyant les avis et en remplaçant les champs vides par des valeurs par défaut.

    Cette fonction prend en entrée une liste de dictionnaires représentant les avis bruts extraits,
    et retourne une nouvelle liste de documents formatés pour Elasticsearch. Les avis vides ou malformés sont
    remplacés par des valeurs par défaut (ex : "indisponible"), et les valeurs numériques sont formatées pour
    correspondre aux attentes d'Elasticsearch (par exemple, les pourcentages sont calculés).

    Parameters
    -----------
    raw_list : List[Dict[str, Any]]
        Une liste de dictionnaires représentant les avis bruts extraits. Chaque dictionnaire
        contient des informations sur les avis ainsi que sur l'entreprise associée.

    Returns
    --------
    List[Dict[str, Any]]
        Une liste de dictionnaires représentant les documents transformés et prêts à être indexés dans Elasticsearch.
        Chaque dictionnaire contient les champs suivants : 'id_review', 'is_verified', 'date_review', 'id_user',
        'user_name', 'user_review', 'user_review_length', 'user_rating', 'date_response', 'enterprise_response',
        ainsi que des informations sur l'entreprise et les pourcentages des différentes notes.
    
    Raises
    -----
    Exception
        Si une erreur survient lors du nettoyage des données ou de l'accès aux clés dans les dictionnaires,
        une exception sera levée.
    """
    all_transformed_reviews: List[Dict[str, Any]] = []

    for raw in raw_list:
        reviews = raw.get("reviews", [])
        enterprise_url: str = raw.get("enterprise_url", "")
        enterprise_info: Dict[str, Any] = raw.get("enterprise", {})

        # Récupération des ratings bruts
        ratings = enterprise_info.get("ratings", {})
        total = ratings.get("total", 0)
        total = max(total, 1)  # évite la division par zéro

        one_star = ratings.get("one", 0)
        two_star = ratings.get("two", 0)
        three_star = ratings.get("three", 0)
        four_star = ratings.get("four", 0)
        five_star = ratings.get("five", 0)

        # Calcul des pourcentages
        pct_one = math.ceil(one_star / total * 100)
        pct_two = math.ceil(two_star / total * 100)
        pct_three = math.ceil(three_star / total * 100)
        pct_four = math.ceil(four_star / total * 100)
        pct_five = math.ceil(five_star / total * 100)

        for review in reviews:
            user = review.get("consumer", {})
            reply = review.get("reply", {})
            dates = review.get("dates", {})
            verification = review.get("labels", {}).get("verification", {})

            # Nettoyage de l'avis utilisateur
            text_clean = DataUtils.clean_text(review.get("text"))
            if not text_clean:
                text_clean = "indisponible"
            review_length = len(text_clean)

            # Nettoyage de la réponse entreprise
            reply_clean = DataUtils.clean_text(reply.get("message") if reply else None)
            if not reply_clean:
                reply_clean = "indisponible"
            else:
                reply_clean = anonymize_enterprise_response(reply_clean)

            all_transformed_reviews.append({
                "id_review": review.get("id"),
                "is_verified": bool(verification.get("isVerified", False)),
                "date_review": DataUtils.format_date(dates.get("publishedDate")),
                "id_user": DataUtils.clean_text(user.get("id")),
                "user_review": text_clean,
                "user_review_length": review_length,
                "user_rating": DataUtils.to_float(review.get("rating")),
                "date_response": DataUtils.format_date(reply.get("publishedDate") if reply else None),
                "enterprise_response": reply_clean,

                # Infos entreprise
                "enterprise_name": DataUtils.clean_text(enterprise_info.get("name") or enterprise_url),
                "enterprise_url": enterprise_url,
                "enterprise_rating": DataUtils.to_float(enterprise_info.get("enterprise_rating")),
                "enterprise_review_number": DataUtils.to_int(enterprise_info.get("enterprise_review_number")),

                # Pourcentages calculés
                "enterprise_percentage_one_star": pct_one,
                "enterprise_percentage_two_star": pct_two,
                "enterprise_percentage_three_star": pct_three,
                "enterprise_percentage_four_star": pct_four,
                "enterprise_percentage_five_star": pct_five,
            })

    return all_transformed_reviews
