from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError, RequestError
from loguru import logger
from load.mapping_reviews import MAPPING_REVIEWS


def create_index_if_not_exists(es: Elasticsearch, index: str = "reviews") -> None:
    """
    Crée un index Elasticsearch s'il n'existe pas déjà.
    Si l'index existe, l'index est supprimé puis recréé.

    :param es: Instance du client Elasticsearch utilisée pour communiquer avec le cluster.
    :type es: Elasticsearch
    :param index: Nom de l'index (collection) Elasticsearch à créer ou vérifier.
    :type index: str
    :return: None

    """
    try:
        if es.indices.exists(index=index):
            logger.info(f"Index {index} a déjà été crée.")
            es.indices.delete(index=index)
            logger.info(f"Index {index} supprimer pour recréation")
        if not es.indices.exists(index=index):
            es.indices.create(index=index, body={"mappings": MAPPING_REVIEWS})
            logger.info(f"Index {index} créer avec succés")
    except RequestError as error:
        logger.exception(
            f"Erreur lors de la création de l'index {index}: {error}")
        raise
    except TransportError as error:
        logger.exception(
            f"Erreur transport Elasticsearch lors de la création de l'index {index}: {error}")
        raise
    except Exception as error:
        logger.exception(
            f"Erreur inattendue lors de la création de l'index {index}: {error}")
        raise
