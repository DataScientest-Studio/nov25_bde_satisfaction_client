# File: src\etl\config\config.py

"""
Module pour configurer les constantes pour l'ETL (Elasticsearch et entreprises)
"""

from typing import List, Dict


ES_HOST: str = "http://elasticsearch:9200"
ENTERPRISES: List[Dict[str, str]] = [
    {"enterprise_url": "www.showroomprive.com"}
]