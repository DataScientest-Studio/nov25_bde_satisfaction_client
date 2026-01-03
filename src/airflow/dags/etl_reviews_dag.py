# File: src\airflow\dags\etl_reviews_dag.py

"""
Ce module définit un DAG Airflow pour exécuter périodiquement le pipeline ETL des avis Trustpilot.
Le DAG est configuré pour s'exécuter toutes les 3 jours à minuit et lance une tâche Bash
qui exécute le script principal du pipeline ETL avec un paramètre spécifiant le nombre de pages à scraper.

Dans ce DAG:
- Le DAG est nommé "etl_reviews_batch".
- La tâche unique "run_etl_reviews" exécute le script ETL avec 10 pages d'avis à récupérer.

A quoi sert catchup=False ? Cela empêche Airflow d'exécuter les instances manquées du DAG pour les intervalles de planification passés.
Pourquoi est-ce important ? Cela évite une surcharge de tâches si le DAG n'a pas été exécuté pendant un certain temps, 
garantissant que seules les exécutions planifiées futures sont prises en compte.

Pourquoi exécuter toutes les 3 jours ? Cela permet de maintenir les données des avis à jour sans surcharger le système
avec des exécutions trop fréquentes, équilibrant ainsi la fraîcheur des données et la charge du système.

pourquoi start_date=datetime(2024, 1, 1) ? Cela définit la date de début du DAG.
Cela signifie que le DAG commencera à s'exécuter à partir du 1er janvier 2024.
Cela permet de contrôler quand le DAG commence à s'exécuter, en évitant les exécutions avant cette date.

"""
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow import DAG
# "*/ * * * *" pour tester toutes les deux minutes

# Définition du DAG Airflow
with DAG(
    dag_id="etl_reviews_batch",
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/2 * * * *",
    catchup=False,
) as dag:
    # Définition de la tâche Bash pour exécuter le script ETL
    run_etl = BashOperator(
        task_id="run_etl_reviews",
        bash_command="PYTHONPATH=/opt/airflow python /opt/airflow/etl/main.py --pages 10",
    )
