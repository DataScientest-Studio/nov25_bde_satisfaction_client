# File: load/elasticsearch_loader.py

"""
Module pour charger des documents dans Elasticsearch via bulk et gérer l'index.

Ce module permet de créer un index Elasticsearch, de vérifier son existence, et d'y insérer des documents
par le biais de l'API 'bulk' d'Elasticsearch. Il gère également les erreurs de connexion et de transport,
ainsi que la suppression et la recréation d'un index si nécessaire.
"""

from typing import List, Dict, Any, Optional
from loguru import logger
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import TransportError, RequestError
from config.config import ES_HOST

logger.info(f"🔌 Utilisation de l'hôte : {ES_HOST}")


def create_index_if_not_exists(
    es: Elasticsearch, index: str = "reviews", delete_if_exists: bool = False
) -> None:
    """
    Crée un index Elasticsearch si celui-ci n'existe pas, ou le recrée si demandé.

    Cette fonction crée l'index Elasticsearch avec un mapping prédéfini si l'index n'existe pas. Si l'index existe
    déjà et que 'delete_if_exists' est 'True', l'index existant est supprimé avant de créer un nouvel index.

    Paramètres:
    -----------
    es : Elasticsearch
        L'instance Elasticsearch à utiliser pour interagir avec le cluster Elasticsearch.
        
    index : str, optionnel
        Le nom de l'index à créer ou à recréer. Par défaut, "reviews".
        
    delete_if_exists : bool, optionnel
        Si 'True', supprime l'index existant avant de créer un nouvel index. Par défaut, 'False'.

    Lève:
    -----
    RequestError
        Si une erreur de requête se produit lors de la création de l'index.
        
    TransportError
        Si une erreur de transport (connexion au cluster Elasticsearch) se produit lors de la création de l'index.
        
    Exception
        Pour toute autre erreur inattendue.
    """
    mapping = {
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "id_review": {"type": "keyword"},
                "is_verified": {"type": "boolean"},
                "date_review": {"type": "date"},
                "id_user": {"type": "keyword"},
                "user_name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
                "user_review": {"type": "text"},
                "user_review_length": {"type": "integer"},
                "user_rating": {"type": "float"},
                "date_response": {"type": "date"},
                "enterprise_name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
                "enterprise_response": {"type": "text"},
                "enterprise_url": {"type": "keyword"},
                "enterprise_rating": {"type": "float"},
                "enterprise_review_number": {"type": "integer"},
                "enterprise_percentage_one_star": {"type": "integer"},
                "enterprise_percentage_two_star": {"type": "integer"},
                "enterprise_percentage_three_star": {"type": "integer"},
                "enterprise_percentage_four_star": {"type": "integer"},
                "enterprise_percentage_five_star": {"type": "integer"},
            },
        }
    }

    try:
        if es.indices.exists(index=index):
            logger.info(f"📁 Index '{index}' existe déjà")
            if delete_if_exists:
                es.indices.delete(index=index)
                logger.info(f"📁 Index '{index}' supprimé pour recréation")

        if not es.indices.exists(index=index):
            es.indices.create(index=index, body=mapping)
            logger.success(f"📁 Index '{index}' créé avec succès")
    except RequestError as e:
        logger.exception(f"❌ Erreur lors de la création de l'index '{index}': {e}")
        raise
    except TransportError as e:
        logger.exception(f"❌ Erreur transport Elasticsearch lors de la création de l'index '{index}': {e}")
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur inattendue lors de la création de l'index '{index}': {e}")
        raise


def load_reviews_to_elasticsearch_bulk(
    docs: List[Dict[str, Any]],
    es_host: Optional[str] = ES_HOST,
    index: str = "reviews",
    delete_index_if_exists: bool = False,
    use_id: bool = True
) -> None:
    """
    Charge une liste de documents dans Elasticsearch via l'API bulk.

    Cette fonction prend une liste de documents et les insère dans Elasticsearch en une seule requête 'bulk'. 
    Si l'index spécifié existe déjà, elle l'utilise. Si l'index n'existe pas, il est créé.
    Les erreurs potentielles pendant l'insertion sont logguées pour chaque document échoué.

    Paramètres:
    -----------
    docs : List[Dict[str, Any]]
        Une liste de dictionnaires représentant les documents à insérer dans Elasticsearch. Chaque dictionnaire
        correspond à un document, et chaque document doit être un ensemble clé-valeur.

    es_host : str, optionnel
        L'hôte de votre serveur Elasticsearch. Par défaut, utilise la valeur configurée dans 'ES_HOST'.

    index : str, optionnel
        Le nom de l'index dans lequel les documents seront insérés. Par défaut, l'index "reviews" est utilisé.

    delete_index_if_exists : bool, optionnel
        Si 'True', l'index existant sera supprimé avant l'insertion des nouveaux documents. Par défaut, 'False'.

    use_id : bool, optionnel
        Si 'True', l'ID du document (clé 'id_review') sera utilisé comme identifiant unique dans Elasticsearch. 
        Par défaut, 'True'.

    Lève:
    -----
    ValueError
        Si 'ES_HOST' n'est pas défini dans les paramètres de configuration.
        
    ConnectionError
        Si la connexion à Elasticsearch échoue.

    RequestError
        Si une erreur de requête se produit lors de l'insertion des documents dans Elasticsearch.
        
    TransportError
        Si une erreur de transport (connexion au cluster Elasticsearch) se produit lors de l'insertion des documents.

    Exception
        Pour toute autre erreur inattendue.
    """
    if not es_host:
        raise ValueError("ES_HOST n'est pas défini")

    # Vérifie la connexion à Elasticsearch et loggue une erreur si elle échoue
    try:
        es = Elasticsearch(es_host)
        if not es.ping():
            raise ConnectionError("Impossible de se connecter à Elasticsearch")
    except Exception as e:
        logger.exception(f"❌ Impossible de se connecter à Elasticsearch: {e}")
        raise

    # Crée l'index Elasticsearch ou loggue une erreur si la création/validation échoue
    try:
        create_index_if_not_exists(es, index=index, delete_if_exists=delete_index_if_exists)
    except Exception as e:
        logger.exception(f"❌ Impossible de créer ou vérifier l'index '{index}': {e}")
        raise

    if not docs:
        logger.warning("Aucun document à insérer dans Elasticsearch")
        return

    # Préparer les actions pour bulk
    actions = []
    for doc in docs:
        action = {"_index": index, "_source": doc}
        if use_id and doc.get("id_review"):
            action["_id"] = doc["id_review"]
        actions.append(action)

    # Exécute l'insertion bulk des documents et loggue le succès ainsi que les éventuelles erreurs
    try:
        success, errors = helpers.bulk(es, actions, raise_on_error=False)
        logger.success(f"🚀 {success} documents insérés dans Elasticsearch (bulk)")
        if errors:
            logger.warning(f"⚠️ {len(errors)} erreurs lors de l'insertion bulk : {errors}")
    except Exception as e:
        logger.exception(f"❌ Erreur critique lors de l'insertion bulk : {e}")
