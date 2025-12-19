# File: src\etl\load\elasticsearch_bulk_loader.py

"""
Module pour le chargement des avis clients dans Elasticsearch via l'API Bulk.

Ce module implémente la phase de chargement (Load) du pipeline ETL.
Il permet d'insérer ou de mettre à jour des documents dans un index
Elasticsearch en utilisant des opérations bulk avec upsert.

Fonctionnalités principales :
- Connexion et vérification de l'accessibilité du cluster Elasticsearch
- Création automatique de l'index s'il n'existe pas
- Chargement massif de documents avec mise à jour ou insertion conditionnelle
  basée sur l'identifiant métier `id_review`
- Journalisation des succès et des erreurs via Loguru
"""

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
    Insère ou met à jour des documents dans Elasticsearch en utilisant le mode bulk (upsert).

    La fonction :
    - Vérifie la connexion au cluster Elasticsearch
    - Crée l'index s'il n'existe pas
    - Effectue un upsert :
        * insertion si le document n'existe pas
        * mise à jour s'il existe déjà (basé sur l'id_review)

    :param documents: Liste des documents à insérer ou mettre à jour
    :type documents: List[Dict[str, Any]]
    :param es_host: URL du cluster Elasticsearch
    :type es_host: Optional[str]
    :param index: Nom de l'index Elasticsearch
    :type index: str
    :param use_id: Utilise le champ `id_review` comme identifiant du document
    :type use_id: bool
    :return: None
    """
    if not es_host:
        raise ValueError("ES_HOST n'est pas défini")

    # Connexion à Elasticsearch
    try:
        es = Elasticsearch(es_host)
        if not es.ping():
            raise ConnectionError("Impossible de se connecter à Elasticsearch")
    except Exception as error:
        logger.exception(
            f"Impossible de se connecter à Elasticsearch: {error}")
        raise

    # Création de l'index si nécessaire
    create_index_if_not_exists(es=es, index=index)

    if not documents:
        logger.warning("Aucun document à insérer ou mettre à jour dans Elasticsearch")
        return

    actions = []

    for document in documents:
        # Vérifie la présence de l'identifiant du document
        if use_id and not document.get("id_review"):
            logger.warning("Document ignoré : champ 'id_review' manquant")
            continue

        # Action bulk en mode update + upsert
        action = {
            "_op_type": "update",
            "_index": index,
            "_id": document["id_review"],
            "doc": document,
            "doc_as_upsert": True  # Crée le document s'il n'existe pas
        }

        actions.append(action)

    # Exécution du bulk upsert
    try:
        success, errors = helpers.bulk(es, actions)
        logger.success(f"{success} documents insérés ou mis à jour dans Elasticsearch")

        if errors:
            logger.warning(
                f"Erreurs rencontrées lors de l'upsert bulk : {errors}")

    except Exception as error:
        logger.exception(
            f"Erreur critique lors de l'upsert bulk : {error}")
        raise
