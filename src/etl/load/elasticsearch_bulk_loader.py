from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError
from typing import List, Dict, Any, Optional
from loguru import logger
from load.create_index_elasticsearch import create_index_if_not_exists


def load_reviews_to_elasticsearch_bulk(
    documents: List[Dict[str, Any]],
    es_host: Optional[str] = "http://localhost:9200/",
    index: str = "reviews",
    use_id: bool = True
) -> None:
    """
    Charge une liste de documents dans Elasticsearch en utilisant bulk.

    La fonction:
    - Vérifie la connexion dans Elasticsearch
    - Crée l'index s'il n'existe pas
    - Insère les documents en une seule requête pour de meilleures performances

    :param documents: Liste de documents à insérer dans Elasticsearch.
    :type documents: List[Dict[str, Any]]
    :param es_host: URL du cluster Elasticsearch.
    :type es_host: Optional[str]
    :param index: Nom de l'index Elasticsearch dans lequel insérer les documents.
    :type index: str
    :param use_id: Indique si le champ `id_review` doit être utilisé comme identifiant du document.
    :type use_id: bool
    :return: None
    """
    if not es_host:
        raise ValueError("ES_HOST n'est pas défini")

    try:
        es = Elasticsearch(es_host)
        if not es.ping():
            raise ConnectionError("Impossible de se connecter à ElasticSearch")
    except Exception as error:
        logger.exception(
            f"Impossible de se connecter à Elasticsearch: {error}")
        raise

    try:
        create_index_if_not_exists(es=es, index=index)
    except Exception as error:
        logger.exception(f"Impossible de créer l'index {index}: {error}")
        raise

    if not documents:
        logger.warning("Aucun document à insérer dans Elasticsearch")
        return

    actions = []

    for document in documents:
        action = {
            "_index": index,
            "_source": document
        }
        if use_id and document.get("id_review"):
            action["_id"] = document["id_review"]
        actions.append(action)
    try:
        success, errors = helpers.bulk(client=es, actions=actions)
        logger.success(f"{success} document insérés dans Elasticsearch")
        if errors:
            logger.warning(
                f"Erreurs lors de l'insertion des documents dans Elasticsearch: {errors}")
    except Exception as error:
        logger.exception(f"Erreur critique lors de l'insertion: {error}")
