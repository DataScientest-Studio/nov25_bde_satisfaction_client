# File: main.py

"""
Main script
-----------
Exécution du pipeline ETL pour récupérer les avis Trustpilot, avec possibilité de définir le nombre de pages à scraper.

Ce script permet de lancer un pipeline ETL complet pour récupérer les avis des entreprises sur Trustpilot. 
Le nombre de pages à scraper peut être spécifié via la ligne de commande.

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
from pipeline.reviews_etl import run_reviews_etl
from loguru import logger


def run_pipeline(pages: int) -> None:
    """
    Lance le pipeline ETL pour récupérer les avis Trustpilot et effectuer les étapes d'extraction, 
    transformation, sauvegarde et chargement.

    Cette fonction appelle le pipeline ETL avec le nombre de pages spécifié à scraper.

    Parameters
    ----------
    pages : int
        Nombre de pages à récupérer par entreprise. Cette valeur est utilisée pour définir la quantité de données à scraper 
        pour chaque entreprise.
    
    Lève
    -----
    Exception
        Si une erreur se produit lors de l'exécution du pipeline ETL (par exemple, une erreur lors de l'extraction, 
        transformation, sauvegarde ou chargement des données).
    """
    logger.info(f"🚀 Exécution du pipeline ETL (pages = {pages})")
    run_reviews_etl(max_pages=pages)


if __name__ == "__main__":
    # Parsing des arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Lancer le pipeline ETL Trustpilot")
    parser.add_argument("--pages", type=int, default=10, help="Nombre de pages d'avis à récupérer")
    
    # Récupération des arguments
    args = parser.parse_args()

    # Lancement du pipeline avec le nombre de pages spécifié
    run_pipeline(args.pages)
