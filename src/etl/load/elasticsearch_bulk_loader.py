# File: src\etl\load\elasticsearch_bulk_loader.py

"""
Module pour le chargement des avis clients dans Elasticsearch via l'API Bulk.

Ce module implémente la phase de chargement (Load) du pipeline ETL.
Il permet d'insérer ou de mettre à jour des documents dans un index
Elasticsearch en utilisant des opérations bulk avec upsert.

Fonctionnalités principales :
- Connexion au cluster Elasticsearch et vérification de sa disponibilité
- Création automatique de l'index si inexistant
- Chargement massif de documents avec upsert (update ou insert)
- Ajout automatique des champs `created_at` et `updated_at` pour le suivi
- Gestion et journalisation des erreurs via Loguru
"""

from datetime import datetime, timezone
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError
from typing import List, Dict, Any, Optional
from loguru import logger
from load.create_index_elasticsearch import create_index_if_not_exists


def load_reviews_to_elasticsearch_bulk(
    documents: List[Dict[str, Any]],
    es_host: Optional[str] = "http://elasticsearch:9200",
    index: str = "reviews",
    use_id: bool = True
) -> None:
    """
    Insère ou met à jour des documents dans Elasticsearch via l'API Bulk (upsert).

    Chaque document sera soit :
    - mis à jour si `id_review` existe déjà dans l'index
    - inséré sinon

    Les champs `created_at` et `updated_at` sont automatiquement gérés :
    - `created_at` ajouté uniquement si le document n'existait pas
    - `updated_at` mis à jour à chaque opération

    :param documents: Liste des documents à insérer ou mettre à jour
    :param es_host: URL du cluster Elasticsearch
    :param index: Nom de l'index Elasticsearch
    :param use_id: Si True, utilise le champ `id_review` comme identifiant
    """
    if not es_host:
        raise ValueError("ES_HOST n'est pas défini")

    # Connexion au cluster Elasticsearch et vérification de la disponibilité
    try:
        es = Elasticsearch(es_host)
        if not es.ping():
            raise ConnectionError("Impossible de se connecter à Elasticsearch")
    except Exception as error:
        logger.exception(
            f"Impossible de se connecter à Elasticsearch: {error}")
        raise

    # Création de l'index si celui-ci n'existe pas déjà
    create_index_if_not_exists(es=es, index=index)

    if not documents:
        logger.warning(
            "Aucun document à insérer ou mettre à jour dans Elasticsearch")
        return

    actions = []

    # Timestamp au format ISO 8601 UTC pour created_at / updated_at
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for document in documents:
        # Ignorer les documents sans identifiant métier si use_id=True
        if use_id and not document.get("id_review"):
            logger.warning("Document ignoré : champ 'id_review' manquant")
            continue

        # Préparer le document avec le champ updated_at
        doc = {**document, "updated_at": now}

        # Préparer la version upsert avec created_at si absent
        upsert_doc = {**doc}
        upsert_doc.setdefault("created_at", now)

        # Construire l'action Bulk pour Elasticsearch
        action = {
            "_op_type": "update",  # type d'opération : upsert
            "_index": index,
            "_id": doc.get("id_review"),
            "doc": doc,           # données à mettre à jour
            "upsert": upsert_doc  # document à créer si inexistant
        }

        actions.append(action)

    # Exécution du bulk upsert avec gestion des erreurs
    try:
        success, errors = helpers.bulk(es, actions, raise_on_error=False)
        logger.success(
            f"{success} documents insérés ou mis à jour dans Elasticsearch")

        if errors:
            logger.warning(
                f"Erreurs rencontrées lors de l'upsert bulk : {errors}")

    except Exception as error:
        logger.exception(
            f"Erreur critique lors de l'upsert bulk : {error}")
        raise
