# NOV25 – BDE Satisfaction Client

## Pipeline ETL Trustpilot → Elasticsearch

Ce dépôt contient un pipeline **Extract – Transform – Load (ETL)** permettant de collecter des avis publiés sur **Trustpilot** et de les indexer dans **Elasticsearch** sous le nom d’indice **`reviews`**. Il inclut :
- Extraction : récupération des avis pour plusieurs entreprises, gestion des pages et filtrage automatique.
- Transformation : nettoyage des textes, parsing des dates et normalisation des données.
- Chargement : insertion dans Elasticsearch et mise à jour incrémentale.

## Stack Docker complet

Le pipeline s’exécute dans un environnement **Docker Compose** pour isoler toutes les dépendances et faciliter le déploiement :

| Service        | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| **Airflow**    | Orchestration des DAGs ETL, planification et exécution du pipeline. |
| **FastAPI**    | API pour l’accès aux données et aux résultats d’analyse.           |
| **Streamlit**  | Dashboard pour visualiser les avis et l’analyse de sentiment.     |
| **Elasticsearch** | Indexation des avis pour recherche et agrégation.                |
| **Kibana**     | Interface de visualisation et exploration des données Elasticsearch. |
| **Grafana**    | Monitoring et dashboards métriques.                                 |
| **Prometheus** | Collecte des métriques des services pour monitoring.               |
| **Node Exporter** | Export des métriques système pour Prometheus.                     |

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Configuration et exécution locale](#2-configuration-et-exécution-locale)
3. [Tests Unitaires](#3-tests-unitaires)
4. [Exécution avec Docker Compose](#4-exécution-avec-docker-compose)
5. [Création d’une vue et d’un tableau de bord dans ES/Kibana](#5-création-dune-vue-et-dun-tableau-de-bord-dans-es-kibana)
6. [Accès à Streamlit](#6-accès-à-streamlit)
7. [Accès à Apache Airflow](#7-accès-à-apache-airflow)
8. [Accès à Prometheus/Grafana](#8-accès-à-prometheus-grafana)
9. [Dépannage & problèmes fréquents](#9-dépannage--problèmes-fréquents)

---

## 1. Prérequis

| Outil          | Version minimale | Obligatoire |
| -------------- | ---------------- | ----------- |
| Python         | 3.10+            | ✅          |
| Docker         | 20.x+            | ✅          |
| Docker Compose | 1.29+            | ✅          |
| Elasticsearch  | 8.12+            | optionnel   |
| Kibana         | 8.12+            | optionnel   |
|**WSL Ubuntu**  | N/A              | ✅          |

---

## 2. Configuration et exécution locale

### 2.1. Création de l’environnement virtuel

   ```bash
   # Depuis la racine du projet
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 3. Tests Unitaires

Les tests du projet sont réalisés avec pytest.</br>
Pour exécuter tous les tests, il suffit de se rendre à la racine du projet et</br>
de lancer la commande suivante :

   ```bash
   source venv/bin/activate
   export PYTHONPATH=$(pwd)/src
   echo $PYTHONPATH
   pytest src/tests
   ```

---

## 4. Exécution avec Docker Compose

### 4.1. Nettoyage complet (optionnel)

⚠️ Attention :</br>
Les commandes suivantes suppriment tous les conteneurs, images et volumes Docker.

1. Arrêt et suppression des conteneurs

   ```bash
   cd src/docker
   docker ps -a -q | xargs -r docker stop
   docker ps -a -q | xargs -r docker rm
   ```

2. Suppression des images

   ```bash
   cd src/docker
   docker images -q | xargs -r docker rmi -f
   ```

3. Suppression des volumes

   ```bash
   cd src/docker
   docker volume ls -q | xargs -r docker volume rm
   ```

4. Nettoyage du dossier data

   ```bash
   cd src/docker
   docker compose down -v
   rm -rf ./data/*
   mkdir -p ./data
   chmod -R 777 ./data
   ```

### 4.2. Construction

   ```bash
   cd src/docker
   docker compose build --no-cache
   chmod +x start_stack.sh
   ./start_stack.sh
   ```

### 4.3. Lancement du Pipeline ETL

Effectuer cette étape manuellement depuis le DAG Airflow

---

## 5. Création d’une vue et d’un tableau de bord dans ES/Kibana

### 5.1. Accès à Kibana

   ```bash
   http://localhost:5601
   ```

### 5.2. Vérification des données

Depuis Kibana – Dev Tools :

   ```bash
   # Liste tous les indices
   GET /_cat/indices?v
   # Voir le mapping d'un index
   GET /reviews/_mapping
   # Compter le nombre de documents
   GET /reviews/_count
   # Récupére tous les documents
   GET /reviews/_search
   {
      "query": {
         "match_all": {}
      }
   }
   # Récupére les 3 dernières reviews les plus récents
   GET reviews/_search
   {
      "size": 3,
      "sort": [
         { "id_review": { "order": "desc" } }
      ]
   }
   ```

### 5.3. Création d’une Data View

   ```bash
   Nom : NOV25_BDE_SATISFACTION_CLIENT
   Index pattern : reviews*
   Champ temporel : Aucun
   ```

### 5.4. Visualisation

1. Accéder à Elastic/Kibana depuis le navigateur : http://localhost:5601/app/home#/

2. Aller dans **Visualize Library** → **Create new visualization**

3. Sélectionner le type de visualisation : **Lens**

4. Choisir la **Data View** précédemment créée (`NOV25_BDE_SATISFACTION_CLIENT`)

5. Créer les visualisations suivantes :

   - **Histogramme des notes** (répartition des avis par score)
   - **Top catégories** (catégories les plus représentées)
   - **Volume d’avis** (nombre total d’avis ou évolution)

6. Enregistrer chaque visualisation pour pouvoir les réutiliser dans un tableau de bord.

### 5.5. Initialisation lors du premier démarrage (Docker)

1. Importer les objets sauvegardés (depuis le menu hamburger) :

   - Stack Management
   - Saved Objects
   - Import
   - Sélectionner le fichier .ndjson
   - Laisser les options par défaut

2. Exécuter le pipeline ETL manuellement depuis le DAG Airflow

3. Depuis Elastic/Kibana, aller dans Analytics :
   - Dashboards et appliquer un filtre sur les 7 derniers jours.

---

## 6. Accès à Streamlit

   ```bash
   http://localhost:8501
   ```

---

## 7. Accès à Apache Airflow

   ```bash
   http://localhost:8081/login/
   ```

   - Identifiant  : admin</br>
   - Mot de passe : admin

---

## 8. Accès à Prometheus/Grafana

- Prometheus :

   ```bash
   http://localhost:9090/targets
   ```

- Grafana :

   ```bash
   http://localhost:3000
   ```

   - Identifiant  : admin</br>
   - Mot de passe : admin

---

## 9. Dépannage & problèmes fréquents

| Problème                           | Cause probable                                     | Solution                                                                                                                                                                                                                               |
| ---------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Elasticsearch ne démarre pas       | Port 9200 utilisé, mémoire insuffisante            | Vérifier les ports et ajuster `docker-compose.yml`                                                                                                                                                                                     |
| ConnectionError vers Elasticsearch | Service ES pas encore prêt                         | Attendre (`sleep 30`) ou ajouter un retry dans le script                                                                                                                                                                               |
| Mapping non appliqué               | Indice existant                                    | Supprimer l’indice : `DELETE /reviews`                                                                                                                                                                                                 |
| Data View introuvable              | Mauvais pattern                                    | Vérifier que le pattern est `reviews*`                                                                                                                                                                                                 |
| Problème de permissions            | Volume Docker                                      | `chmod -R 777 ./data`                                                                                                                                                                                                                  |
| Erreur Docker sous Windows         | Docker Desktop non démarré ou backend WSL2 inactif | Vérifier que **Docker Desktop** est démarré, que le backend **WSL2** est actif, puis relancer Docker Desktop. Message typique : `unable to get image docker.elastic.co/kibana/kibana:8.12.0 The system cannot find the file specified` |
