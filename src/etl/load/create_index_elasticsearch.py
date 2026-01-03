# File: src\etl\load\create_index_elasticsearch.py

"""
Module pour la création et gestion de l'index Elasticsearch pour les avis clients.

Ce module fournit une fonction utilitaire permettant de créer un index
Elasticsearch uniquement s'il n'existe pas déjà. L'index est initialisé
avec le mapping strict défini dans `MAPPING_REVIEWS`.

Il est utilisé lors de la phase de chargement (Load) du pipeline ETL afin
de garantir que la structure de l'index est conforme avant toute insertion
ou mise à jour de documents.
"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, RequestError
from loguru import logger
from etl.load.mapping_reviews import MAPPING_REVIEWS


def create_index_if_not_exists(es: Elasticsearch, index: str = "reviews") -> None:
    """
    Crée l'index Elasticsearch s'il n'existe pas déjà.

    - Si l'index existe : aucune action n'est effectuée
    - Si l'index n'existe pas : il est créé avec le mapping défini

    :param es: Instance du client Elasticsearch
    :type es: Elasticsearch
    :param index: Nom de l'index Elasticsearch
    :type index: str
    :return: None
    """
    try:
        if not es.indices.exists(index=index):
            es.indices.create(index=index, body={"mappings": MAPPING_REVIEWS})
            logger.success(f"Index '{index}' créé avec succès")
        else:
            logger.info(f"Index '{index}' existe déjà, création ignorée")

    except RequestError as error:
        logger.exception(
            f"Erreur lors de la création de l'index '{index}': {error}")
        raise
    except TransportError as error:
        logger.exception(
            f"Erreur de transport Elasticsearch lors de la création de l'index '{index}': {error}")
        raise
    except Exception as error:
        logger.exception(
            f"Erreur inattendue lors de la création de l'index '{index}': {error}")
        raise
