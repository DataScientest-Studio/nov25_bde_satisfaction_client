from typing import List, Dict
import os
from loguru import logger
import json


def load_last_jsonl(folder: str) -> List[Dict]:
    """
    Charge le fichier JSONL le plus récent présent dans un dossier.

    La fonction:
    - Recherche tous les fichiers ".jsonl" dans le dossier fourni
    - Selectionne le plus récent selon la date de modification
    - Lit chaque ligne du fichier et la convertit en dictionnaire

    :param folder: Chemin du dossier contenant les fichiers JSONL.
    :type folder: str
    :return: Liste de documents chargés depuis le fichier JSONL le plus récent.
    :rtype: List[Dict]
    :raises FileNotFoundError: Si aucun fichier JSONL n'est trouvé dans le dossier.
    :raises Exception: Si une erreur survient lors de l'accès au dossier ou du chargement du fichier.
    """

    try:
        files = [file for file in os.listdir(
            folder) if file.endswith(".jsonl")]
    except Exception as error:
        logger.error(f"Erreur d'accès au dossier {folder}: {error}")
        raise

    if not files:
        logger.error(f"Aucun fichier jsonl trouvé dans le dossier {folder}")
        raise FileNotFoundError("Aucun fichier jsonl trouvé dans le dossier")

    try:
        files.sort(
            key=lambda filename: os.path.getmtime(
                os.path.join(folder, filename)),
            reverse=True
        )
        last_file = os.path.join(folder, files[0])

        documents: List[Dict] = []

        with open(last_file, "r", encoding="utf-8") as file:
            for line in file:
                documents.append(json.loads(line))
        return documents
    except Exception as error:
        logger.error(
            f"Erreur lors du chargement du jsonl {last_file}: {error}")
        raise
