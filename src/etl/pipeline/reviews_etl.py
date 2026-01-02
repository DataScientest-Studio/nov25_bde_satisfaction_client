# File: src\etl\pipeline\reviews_etl.py

"""
Module pour exécuter l'ETL des avis Trustpilot (extraction, transformation, sauvegarde et chargement).

Ce module orchestre l'ensemble du processus ETL pour les avis Trustpilot : 
1. Extraction des avis depuis Trustpilot.
2. Transformation des données brutes en documents adaptés pour Elasticsearch.
3. Sauvegarde des données transformées au format JSONL.
4. Chargement des données dans Elasticsearch via une insertion en bulk.

Le processus peut être configuré pour exécuter uniquement certaines étapes selon les besoins.
"""

import asyncio
from typing import List, Dict
from loguru import logger
from src.etl.extract.reviews_scraper import get_reviews_from_trustpilot
from src.etl.transform.transform_reviews import transform_reviews_for_elasticsearch
from src.etl.load.elasticsearch_bulk_loader import load_reviews_to_elasticsearch_bulk
from src.etl.utils.files_utils import FileUtils


def run_reviews_etl(
    max_pages: int,
    do_extract: bool = True,
    do_transform: bool = True,
    do_save: bool = True,
    do_load: bool = True
) -> None:
    """
    Lance le pipeline ETL complet des avis Trustpilot avec des options pour exécuter chaque étape.

    Ce pipeline est constitué de plusieurs étapes : extraction, transformation, sauvegarde et chargement.
    Chaque étape peut être activée ou désactivée en fonction des besoins via les paramètres 'do_extract',
    'do_transform', 'do_save', et 'do_load'.

    Parameters
    -----------
    max_pages : int, optionnel
        Le nombre maximal de pages d'avis à extraire depuis Trustpilot. Par défaut, 1.

    do_extract : bool, optionnel
        Si 'True', l'extraction des avis depuis Trustpilot est effectuée. Par défaut, 'True'.

    do_transform : bool, optionnel
        Si 'True', les avis extraits sont transformés en documents compatibles avec Elasticsearch. Par défaut, 'True'.

    do_save : bool, optionnel
        Si 'True', les données transformées sont sauvegardées au format JSONL. Par défaut, 'True'.

    do_load : bool, optionnel
        Si 'True', les documents transformés sont chargés dans Elasticsearch via l'API 'bulk'. Par défaut, 'False'.

    Raises
    -----
    Exception
        Si une erreur se produit à n'importe quelle étape du pipeline (extraction, transformation, sauvegarde, chargement).
    """
    logger.info(f"Démarrage du pipeline ETL Reviews (pages={max_pages})")

    extract_raw: List[Dict] = []
    transform_docs: List[Dict] = []

    # ---- Extraction ----
    if do_extract:
        try:
            logger.info("[1/4] Extraction des avis...")
            extract_raw = asyncio.run(
                get_reviews_from_trustpilot(max_pages=max_pages))

            # Sauvegarde via FileUtils
            FileUtils.save_to_json(extract_raw, "extract_raw")

            logger.success(
                f"Extraction terminée : {len(extract_raw)} reviews récupérées")
        except Exception as e:
            logger.exception(f"✖ Erreur lors de l'extraction : {e}")

    # ---- Transformation ----
    if do_transform:
        try:
            if not extract_raw:
                logger.warning(
                    "⚠️ Aucune donnée brute trouvée, tentative de charger dernier JSON...")
                extract_raw = FileUtils.load_last_jsonl("data")
                if not extract_raw:
                    raise ValueError("Aucune donnée à transformer")

            logger.info("[2/4] Transformation des avis...")
            transform_docs = transform_reviews_for_elasticsearch(extract_raw)
            logger.success(
                f"Transformation terminée : {len(transform_docs)} documents prêts pour Elasticsearch")
        except Exception as e:
            logger.exception(f"✖ Erreur lors de la transformation : {e}")

    # ---- Sauvegarde JSONL ----
    if do_save:
        try:
            if not transform_docs:
                logger.warning(
                    "Aucun document transformé trouvé, tentative de charger dernier JSON...")
                transform_docs = FileUtils.load_last_jsonl("data")
                if not transform_docs:
                    raise ValueError("Aucune donnée à sauvegarder")

            logger.info("[3/4] Sauvegarde en JSONL...")
            jsonl_path = FileUtils.save_to_jsonl(transform_docs, "reviews")
            logger.info(f"Données sauvegardées : {jsonl_path}")
        except Exception as e:
            logger.exception(f"✖ Erreur lors de la sauvegarde JSONL : {e}")

    # ---- Chargement Elasticsearch ----
    if do_load:
        try:
            if not transform_docs:
                logger.warning(
                    "Aucun document trouvé, tentative de charger dernier JSON...")
                transform_docs = FileUtils.load_last_jsonl("data")
                if not transform_docs:
                    raise ValueError(
                        "Aucun document à charger dans Elasticsearch")

            logger.info("[4/4] Chargement vers Elasticsearch...")
            load_reviews_to_elasticsearch_bulk(transform_docs, index="reviews")
            logger.success("Chargement Elasticsearch terminé")
        except Exception as e:
            logger.exception(
                f"✖ Erreur lors du chargement Elasticsearch : {e}")
