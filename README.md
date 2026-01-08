# NOV25 – BDE Satisfaction Client

## Schéma d'architecture du projet

![Schéma d'architecture du projet](images\architecture_projet_satisfaction_client.png)

## Site d'avis de clients → Pipeline ETL → Elasticsearch

Ce dépôt contient un pipeline **ETL (Extract – Transform – Load)** conçu pour collecter des avis publiés et les indexer dans **Elasticsearch** sous l’indice **`reviews`**. Il comprend les étapes suivantes :

### Extraction
- Récupération des avis pour une ou plusieurs entreprises (dans ce projet, une seule entreprise).
- Gestion automatique de la pagination pour collecter tous les avis disponibles.
- Filtrage et traitement initial des données afin d’assurer la qualité et la cohérence.

### Transformation
- Anonymisation des informations personnelles pour respecter le **RGPD**.
- Nettoyage et normalisation des textes.
- Parsing des dates et formatage des champs pour correspondre aux standards Elasticsearch.
- Préparation des données pour un chargement efficace et incrémental.

### Chargement
- Insertion des données dans Elasticsearch via des opérations **bulk** pour optimiser la performance.
- Mise à jour incrémentale (**upsert**) pour éviter les doublons et maintenir l’indice à jour.
- Gestion des erreurs et logs détaillés pour faciliter le suivi et le débogage.

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

| Outil          | Version | Obligatoire |
| -------------- | ------- | ----------- |
| Python         | 3.10+   | ✅         |
| Docker         | 20.x+   | ✅         |
| Docker Compose | 2.20+   | ✅         |
| Elasticsearch  | 8.12    | optionnel  |
| Kibana         | 8.12    | optionnel  |
|**WSL Ubuntu**  | 2.6+    | ✅         |

---

## 2. Configuration et exécution locale

### 2.1. Création de l’environnement virtuel

   ```bash
   # Sous WSL Ubuntu depuis la racine du projet
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
   # Sous WSL Ubuntu depuis la racine du projet
   source venv/bin/activate
   export PYTHONPATH=$(pwd)/src
   echo $PYTHONPATH
   pytest src/tests
   ```

---

## 4. Exécution avec Docker Compose

⚠️ **Attention** :</br>
   - Les commandes ci-dessous suppriment tous les conteneurs, images et volumes Docker liés au stack, et réinitialise toutes les données persistantes.
Utilisez-la uniquement si vous voulez repartir complètement à zéro ou pour votre première exécution du stack.

   - Si ce script est modifié sous Windows (VS Code),
exécuter `dos2unix start_stack.sh` avant de lancer le script

   ```bash
   cd src/docker
   docker volume prune -f
   docker image prune -a -f
   docker network prune -f
   docker container prune -f
   docker system prune -a -f --volumes
   docker-compose down --volumes --rmi all --remove-orphans
   docker buildx prune -a -f
   ```

   ```bash
   cd src/docker

   # Sous WSL Ubuntu depuis la racine du projet
   chmod +x start_stack.sh
   ./start_stack.sh

   # Sous Windows (PowerShell en mode admin)
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\start_stack.ps1
   ```

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
| `invalid character '/' after object key:value pair` | Fichier `~/.docker/config.json` invalide (commentaire ou syntaxe non JSON) | Éditer `~/.docker/config.json` et supprimer tout commentaire ou caractère invalide. Exemple minimal : <br>```json { "auths": {} }``` <br>Tester ensuite avec `docker pull python:3.10-slim` et `docker pull apache/airflow:2.8.1` |
