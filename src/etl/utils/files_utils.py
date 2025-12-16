# File: utils/files_utils.py

"""
Module utilitaire pour gérer les opérations de fichiers : chargement, lecture, écriture, et génération de timestamps.

Ce module contient des méthodes pour lire et écrire des fichiers au format JSON et JSONL, ainsi que pour générer des 
timestamps uniques pour nommer les fichiers. Il permet aussi de charger des fichiers SQL et de récupérer le dernier 
fichier JSONL d'un dossier donné.
"""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict
from loguru import logger


class FileUtils:
    """Classe utilitaire pour la gestion de fichiers : lecture, écriture et génération de timestamps."""

    @staticmethod
    def get_timestamp() -> str:
        """
        Retourne un timestamp au format 'YYYYMMDD_HHMMSS' représentant la date et l'heure actuelles.

        Cette méthode génère un timestamp qui peut être utilisé pour nommer des fichiers de manière unique.

        Retourne:
        --------
        str
            Le timestamp au format 'YYYYMMDD_HHMMSS' (ex : '20231212_143000').

        Lève:
        -----
        Aucune exception levée. La méthode retourne simplement un timestamp formaté.
        """
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def load_sql_file(path: str) -> str:
        """
        Charge et retourne le contenu d'un fichier SQL spécifié par son chemin.

        Paramètres:
        -----------
        path : str
            Le chemin vers le fichier SQL à charger.

        Retourne:
        --------
        str
            Le contenu du fichier SQL sous forme de chaîne de caractères.

        Lève:
        -----
        FileNotFoundError
            Si le fichier n'est pas trouvé à l'emplacement spécifié.
        Exception
            Si une erreur se produit lors de la lecture du fichier.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Fichier SQL introuvable : {path}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier SQL : {e}")
            raise

    @staticmethod
    def load_last_jsonl(folder: str) -> List[Dict]:
        """
        Charge le dernier fichier JSONL présent dans un dossier spécifié.

        Cette méthode parcourt le dossier donné, identifie le fichier JSONL le plus récent (basé sur la date de 
        modification) et charge son contenu sous forme de liste de dictionnaires.

        Paramètres:
        -----------
        folder : str
            Le chemin du dossier contenant les fichiers JSONL.

        Retourne:
        --------
        List[Dict]
            Une liste de dictionnaires contenant les données lues depuis le dernier fichier JSONL.

        Lève:
        -----
        FileNotFoundError
            Si aucun fichier JSONL n'est trouvé dans le dossier.
        Exception
            Si une erreur se produit lors du chargement du fichier JSONL.
        """
        try:
            files = [f for f in os.listdir(folder) if f.endswith(".jsonl")]
        except Exception as e:
            logger.error(f"Erreur d'accès au dossier {folder} : {e}")
            raise

        if not files:
            msg = f"Aucun fichier JSONL trouvé dans {folder}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        try:
            files.sort(
                key=lambda x: os.path.getmtime(os.path.join(folder, x)),
                reverse=True,
            )
            last_file = os.path.join(folder, files[0])
            docs: List[Dict] = []
            with open(last_file, "r", encoding="utf-8") as f:
                for line in f:
                    docs.append(json.loads(line))
            return docs
        except Exception as e:
            logger.error(f"Erreur lors du chargement du JSONL {last_file} : {e}")
            raise

    @staticmethod
    def save_to_json(data: dict, filename: str) -> Path:
        """
        Enregistre un dictionnaire dans un fichier JSON avec indentation et encodage UTF-8.

        Cette méthode enregistre les données dans un fichier JSON sous le dossier 'data' en utilisant un nom de 
        fichier généré avec un timestamp pour assurer l'unicité.

        Paramètres:
        -----------
        data : dict
            Le dictionnaire contenant les données à enregistrer.
        
        filename : str
            Le nom de fichier de base, auquel sera ajouté un timestamp.

        Retourne:
        --------
        Path
            Le chemin vers le fichier JSON nouvellement créé.

        Lève:
        -----
        Exception
            Si une erreur se produit lors de la création ou de l'écriture du fichier JSON.
        """
        try:
            Path("data").mkdir(exist_ok=True)
            filepath = Path("data") / f"{filename}_{FileUtils.get_timestamp()}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Fichier JSON sauvegardé : {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde JSON {filename} : {e}")
            raise

    @staticmethod
    def save_to_jsonl(docs: List[Dict], filename: str) -> Path:
        """
        Enregistre une liste de dictionnaires dans un fichier JSONL.

        Cette méthode enregistre chaque dictionnaire de la liste dans une nouvelle ligne du fichier JSONL sous le 
        dossier 'data', avec un nom de fichier unique basé sur un timestamp.

        Paramètres:
        -----------
        docs : List[Dict]
            La liste de dictionnaires à enregistrer dans le fichier JSONL.
        
        filename : str
            Le nom de fichier de base, auquel sera ajouté un timestamp.

        Retourne:
        --------
        Path
            Le chemin vers le fichier JSONL nouvellement créé.

        Lève:
        -----
        Exception
            Si une erreur se produit lors de la création ou de l'écriture du fichier JSONL.
        """
        try:
            Path("data").mkdir(exist_ok=True)
            filepath = Path("data") / f"{filename}_{FileUtils.get_timestamp()}.jsonl"
            with open(filepath, "w", encoding="utf-8") as f:
                for doc in docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            return filepath
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde JSONL {filename} : {e}")
            raise
