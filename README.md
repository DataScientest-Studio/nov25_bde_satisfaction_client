# NOV25 – BDE Satisfaction Client

🚀 Présentation du projet

Cette plateforme permet d’automatiser l’analyse de la satisfaction client à partir d’avis en ligne.
Elle couvre l’ensemble de la chaîne data engineering & machine learning, de la collecte des données jusqu’à leur exposition via une API et une interface de visualisation interactive.

Le projet a été réalisé dans le cadre du Bootcamp Data Engineer – DataScientest, avec une approche agile, orientée scalabilité, automatisation et observabilité.

🎯 Objectifs

- Collecter automatiquement des avis clients à grande échelle
- Analyser le sentiment des avis via un modèle de Machine Learning / NLP
- Stocker et indexer les données dans une architecture NoSQL
- Exposer les données via une API REST
- Proposer des dashboards interactifs pour l’exploration des résultats
- Mettre en place orchestration, monitoring et déploiement conteneurisé

🏗️ Architecture du projet

![Schéma d'architecture du projet](images/architecture_projet_satisfaction_client.png)

🔄 Pipeline ETL – Avis clients → Elasticsearch

Ce dépôt contient un pipeline ETL (Extract – Transform – Load) permettant de collecter des avis clients et de les indexer dans Elasticsearch (indice `reviews`).

🔹 Extraction

- Collecte des avis pour une ou plusieurs entreprises (une entreprise dans ce projet)
- Gestion automatique de la pagination
- Validation et filtrage initial des données

🔹 Transformation

- Anonymisation des données sensibles (conformité RGPD)
- Nettoyage et normalisation des textes
- Parsing et standardisation des dates
- Enrichissement et structuration des documents pour Elasticsearch

🔹 Chargement

- Indexation via opérations bulk pour de meilleures performances
- Mécanisme d’upsert pour éviter les doublons
- Logs détaillés et gestion des erreurs pour le suivi du pipeline

🐳 Environnement Docker & Services

L’ensemble du projet est déployé via Docker Compose, garantissant la portabilité et l’isolation des services.

| Service          | Rôle                                                        |
|------------------|-------------------------------------------------------------|
| **Airflow**      | Orchestration et planification des DAGs ETL                 |
| **FastAPI**      | API REST pour l’accès aux données et résultats d’analyse    |
| **Streamlit**    | Interface utilisateur et dashboards interactifs             |
| **Elasticsearch**| Stockage, recherche et agrégation des avis                  |
| **Kibana**       | Exploration et visualisation des données Elasticsearch      |
| **Prometheus**   | Collecte des métriques applicatives                         |
| **Grafana**      | Monitoring et dashboards de supervision                     |
| **Node Exporter**| Collecte des métriques système                              |

🧰 Stack technique

- Langage : Python
- Data Engineering : Airflow, ETL, Elasticsearch
- Machine Learning / NLP : Analyse de sentiment
- Backend : FastAPI
- Frontend : Streamlit
- Conteneurisation : Docker, Docker Compose
- Observabilité : Prometheus, Grafana

👥 Équipe projet

ibbouM  
roxfr Thierry M  
SofianeDore

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
   # Docker Desktop doit être démarré
   # Depuis la racine du projet

   # WSL Ubuntu (terminal)
   cd src/docker
   chmod +x start_stack.sh
   ./start_stack.sh

   # Windows (PowerShell admin)
   cd src\docker
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

| Problème                  | Cause probable                   | Solution                                               |
| ------------------------- | -------------------------------- | ----------------------------------------------------- |
| ES ne démarre pas          | Port 9200 utilisé, mémoire faible | Vérifier ports et ajuster `docker-compose.yml`       |
| ConnectionError ES         | Service ES pas encore prêt       | Attendre 30s ou ajouter un retry                     |
| Mapping non appliqué       | Indice existant                  | Supprimer l’indice : `DELETE /reviews`              |
| Data View introuvable      | Mauvais pattern                  | Vérifier que le pattern est `reviews*`              |
| Problème de permissions    | Volume Docker                    | `chmod -R 777 ./data`                                |
| Docker sous Windows        | Docker Desktop ou WSL2 inactif   | Vérifier Docker Desktop et WSL2, puis relancer      |
| Invalid char '/' config.json | `~/.docker/config.json` invalide | Supprimer tout commentaire et garder `{ "auths": {} }` |
| WSL + Docker login échoue  | Credential helper mal configuré | Supprimer entrées invalides, garder `{ "auths": {} }`, refaire `docker login` |
