# File: main.py

"""
Main script
-----------
Exécution du pipeline ETL pour récupérer les avis Trustpilot, avec possibilité de définir
le nombre de pages à scraper.

Ce script permet de lancer un pipeline ETL complet pour récupérer les avis des entreprises
sur Trustpilot. Le nombre de pages à scraper peut être spécifié via la ligne de commande.

Le pipeline ETL inclut les étapes suivantes :
1. Extraction des avis depuis Trustpilot.
2. Transformation des avis pour les rendre compatibles avec Elasticsearch.
3. Sauvegarde des données en format JSONL.
4. Chargement des données dans Elasticsearch.

Usage :
------
python main.py --pages <nombre_de_pages>
"""

import argparse
from loguru import logger
from pipeline.reviews_etl import run_reviews_etl

# Nombre maximum de pages autorisé
MAX_PAGES = 10


def run_pipeline(pages: int) -> None:
    """
    Lance le pipeline ETL pour récupérer les avis Trustpilot et effectuer les étapes
    d'extraction, transformation, sauvegarde et chargement.

    Parameters
    ----------
    pages : int
        Nombre de pages à récupérer par entreprise.
    """
    if pages > MAX_PAGES:
        logger.warning(
            f"Nombre de pages demandé ({pages}) supérieur au maximum autorisé ({MAX_PAGES}). "
            f"Valeur ramenée à {MAX_PAGES}."
        )
        pages = MAX_PAGES

    logger.info(f"Exécution du pipeline ETL (pages = {pages})")
    run_reviews_etl(max_pages=pages)


if __name__ == "__main__":
    # Parsing des arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Lancer le pipeline ETL Trustpilot")
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help=f"Nombre de pages d'avis à récupérer (max {MAX_PAGES})"
    )

    # Récupération des arguments
    args = parser.parse_args()

    # Lancement du pipeline
    run_pipeline(args.pages)
