# File: src\etl\extract\reviews_scraper.py

"""
Module pour scraper les avis Trustpilot d'une ou plusieurs entreprises.

Ce module permet d'extraire les avis Trustpilot à partir de l'URL d'une entreprise,
en utilisant l'API de Trustpilot, tout en gérant la pagination et les erreurs éventuelles.

Les avis sont récupérés par pages, avec un maximum configurable par entreprise.
"""

import json
import asyncio
from typing import List, Dict
from loguru import logger
from parsel import Selector
from etl.utils.http_client import HttpClient
from etl.config.config import ENTERPRISES

client = HttpClient.get_client()

logger.info(f"Entreprises configurées : {[e['enterprise_url'] for e in ENTERPRISES]}")

async def get_reviews_url_api(url_base: str) -> str:
    """
    Génére l'URL de l'API Trustpilot pour récupérer les avis d'une entreprise.

    Cette fonction extrait dynamiquement le 'buildId' de la page HTML de l'entreprise
    et construit l'URL de l'API Trustpilot pour accéder aux avis.

    Parameters
    ----------
    url_base : str
        L'URL de la page de l'entreprise sur Trustpilot (par exemple : "https://www.trustpilot.com/review/enterprise_url").
        
    Returns
    -------
    str
        L'URL complète de l'API Trustpilot pour récupérer les avis de l'entreprise.
        
    Raises
    -----
    RuntimeError
        Si l'URL de l'API ne peut être générée (par exemple si le 'buildId' est introuvable).
    """
    try:
        response = await client.get(url_base)
        selector = Selector(response.text)
        raw_data = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        if not raw_data:
            raise RuntimeError(f"__NEXT_DATA__ introuvable sur {url_base}")
        build_id = json.loads(raw_data)["buildId"]
        business_unit = url_base.split("review/")[-1]
        # Construction de l'URL de l'API interne Trustpilot (Next.js)
        # - build_id      : identifiant dynamique de build extrait de la page HTML
        # - business_unit : identifiant de l'entreprise sur Trustpilot
        # - sort=recency  : tri des avis par date la plus récente
        # - languages=fr  : récupération des avis en français uniquement
        url_api = (
            f"https://www.trustpilot.com/_next/data/{build_id}/review/"
            f"{business_unit}.json?sort=recency&businessUnit={business_unit}&languages=fr"
        )
        return url_api
    except Exception as e:
        logger.exception(f"[get_reviews_url_api] Impossible de générer l'API URL pour {url_base}: {e}")
        raise

async def scrape_reviews(url_base: str, max_pages: int = 1) -> List[Dict]:
    """
    Récupère et agrège les avis depuis l'API Trustpilot avec gestion de la pagination.

    Cette fonction effectue un scraping des avis d'une entreprise en plusieurs pages si nécessaire.
    Les résultats sont retournés sous forme de liste d'objets JSON contenant les avis.

    Parameters
    ----------
    url_base : str
        L'URL de la page de l'entreprise sur Trustpilot (par exemple : "https://www.trustpilot.com/review/enterprise_url").
        
    max_pages : int, optionnel
        Le nombre maximal de pages à récupérer. Par défaut, 1.

    Returns
    -------
    List[Dict]
        Une liste de dictionnaires représentant les avis récupérés. Chaque dictionnaire contient les informations sur un avis (note, date, etc.).

    Raises
    -----
    Exception
        Si un problème survient lors de la récupération des avis ou de la gestion de la pagination.
    """
    try:
        url_api = await get_reviews_url_api(url_base)
    except Exception:
        logger.error(f"[scrape_reviews] Erreur génération URL API {url_base}")
        return []

    # ---- Première page ----
    try:
        first_page = await client.post(url_api)
        first_page.raise_for_status()
        data = json.loads(first_page.text)["pageProps"]
        reviews_data: List[Dict] = data["reviews"]
        total_pages = data["filters"]["pagination"]["totalPages"]

        if max_pages and max_pages < total_pages:
            total_pages = max_pages
        logger.info(f"Total pages à scraper : {total_pages}")

    except Exception as e:
        logger.error(f"[scrape_reviews] Erreur première page {url_base}: {e}")
        return []

    # ---- Pages suivantes ----
    other_pages = [client.post(url_api + f"&page={page_number}") for page_number in range(2, total_pages + 1)]

    for page_number, response_future in zip(range(2, total_pages + 1), asyncio.as_completed(other_pages)):
        logger.info(f"Scraping de la page {page_number} / {total_pages}")
        try:
            response = await response_future
            response.raise_for_status()
            data = json.loads(response.text)
            if "reviews" in data["pageProps"]:
                page_data = data["pageProps"]["reviews"]
                reviews_data.extend(page_data)
                logger.info(f"Page {page_number}: {len(page_data)} avis récupérés")
            else:
                logger.error(f"Pas de 'reviews' trouvées pour la page {page_number}")

        except Exception as e:
            logger.error(f"[scrape_reviews] Erreur page {page_number}: {e}")

    logger.info(f"Extraction terminée : {len(reviews_data)} avis récupérés")
    return reviews_data


async def get_reviews_from_trustpilot(max_pages: int) -> List[Dict]:
    """
    Récupère les avis et les informations statiques pour toutes les entreprises configurées.

    Cette fonction itère sur les entreprises configurées dans le fichier 'config.py' et récupère les avis
    pour chacune d'elles en utilisant la fonction 'scrape_reviews'. Elle récupère également les statistiques
    globales des avis (note moyenne, nombre d'avis, etc.) pour chaque entreprise.

    Parameters
    ----------
    max_pages : int, optionnel
        Le nombre maximal de pages à récupérer pour chaque entreprise. Par défaut, 1.

    Returns
    -------
    List[Dict]
        Une liste de dictionnaires contenant les résultats du scraping pour chaque entreprise. 
        Chaque dictionnaire contient :
        - 'enterprise_url': URL de l'entreprise sur Trustpilot.
        - 'enterprise': Informations générales sur l'entreprise (note moyenne, nombre d'avis, etc.).
        - 'reviews': Liste des avis récupérés sous forme de dictionnaires.

    Raises
    -----
    Exception
        Si un problème survient lors du scraping pour une entreprise spécifique.
    """
    results = []

    if not ENTERPRISES:
        logger.warning("Aucune entreprise configurée pour le scraping")
        return results

    # Boucle sur les entreprises (dans notre cas : une seule entreprise)
    for enterprise in ENTERPRISES:
        enterprise_url = enterprise.get("enterprise_url")
        if not enterprise_url:
            logger.warning("Enterprise sans 'enterprise_url' ignorée")
            continue

        url_base = f"https://www.trustpilot.com/review/{enterprise_url}"

        try:
            # Scraping des avis par page
            reviews_data = await scrape_reviews(url_base, max_pages)

            # Récupération des infos statiques
            url_api = await get_reviews_url_api(url_base)
            first_page = await client.post(url_api)
            first_page.raise_for_status()
            page_props = json.loads(first_page.text)["pageProps"]

            # Extraction brute des stats
            review_stats = page_props.get("filters", {}).get("reviewStatistics", {})
            ratings = review_stats.get("ratings", {})
            enterprise_info = {
                "enterprise_rating": page_props.get("businessUnit", {}).get("trustScore"),
                "enterprise_review_number": page_props.get("businessUnit", {}).get("numberOfReviews"),
                "ratings": ratings,
                "name": page_props.get("businessUnit", {}).get("displayName") or enterprise_url
            }

            # Ajout dans résultat
            results.append({
                "enterprise_url": enterprise_url,
                "enterprise": enterprise_info,
                "reviews": reviews_data
            })

        except Exception as e:
            logger.error(f"[get_reviews_from_trustpilot] Erreur scraping {url_base}: {e}")
            results.append({
                "enterprise_url": enterprise_url,
                "enterprise": {},
                "reviews": []
            })

    return results
