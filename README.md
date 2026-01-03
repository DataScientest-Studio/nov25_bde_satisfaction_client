# NOV25 – BDE Satisfaction Client

## Pipeline ETL Trustpilot → Elasticsearch

Ce dépôt contient un pipeline **Extract – Transform – Load (ETL)** permettant de récupérer des avis publiés sur **Trustpilot** et de les indexer dans **Elasticsearch** sous le nom d’indice **`reviews`**.

Le projet peut être exécuté de deux manières :

| Mode                | Avantages                                                 |
| ------------------- | --------------------------------------------------------- |
| Local (sans Docker) | Débogage rapide, aucun service externe requis             |
| Docker Compose      | Isolation des dépendances, idéal pour CI/CD et production |

---

## Table des matières

1. [Prérequis](#1-prérequis)
2. [Exécution locale](#2-configuration-et-exécution-locale)
3. [Exécution avec Docker Compose](#3-exécution-avec-docker-compose)
4. [Vérification des données](#4-vérification-des-données)
5. [Kibana – Data View et Dashboard](#5-kibana--création-dune-vue-et-dun-tableau-de-bord)
6. [Accès à l’application Streamlit (Frontend)](#6-accès-à-lapplication-streamlit-frontend)
7. [Tests Unitaires](#7-tests-unitaires)
8. [Dépannage & problèmes fréquents](#8-dépannage--problèmes-fréquents)

---

## 1. Prérequis

| Outil          | Version minimale | Obligatoire |
| -------------- | ---------------- | ----------- |
| Python         | 3.10+            | ✅          |
| Docker         | 20.x+            | ✅          |
| Docker Compose | 1.29+            | ✅          |
| Elasticsearch  | 8.12+            | optionnel   |
| Kibana         | 8.12+            | optionnel   |
|**WSL UBUNTU**  |                  |             |

---

## 2. Configuration et exécution locale

### 2.1 Création de l’environnement virtuel

   ```bash
   # Depuis la racine du projet
   python3 -m venv venv

   # Pour macOS / Linux
   source venv/bin/activate

   # Installation des dépendances
   pip install --upgrade pip

   pip install -r requirements.txt
   ```

---

## 3. Exécution avec Docker Compose

### 3.1 Nettoyage complet (optionnel)

⚠️ Attention :
Les commandes suivantes suppriment tous les conteneurs, images et volumes Docker.

# Arrêt et suppression des conteneurs

   ```bash
   cd src/docker
   docker ps -a -q | xargs -r docker stop
   docker ps -a -q | xargs -r docker rm
   ```

# Suppression des images

   ```bash
   cd src/docker
   docker images -q | xargs -r docker rmi -f
   ```

# Suppression des volumes

   ```bash
   cd src/docker
   docker volume ls -q | xargs -r docker volume rm
   ```

# Nettoyage du dossier data

   ```bash
   cd src/docker
   docker compose down -v
   rm -rf ./data/*
   mkdir -p ./data
   chmod -R 777 ./data
   ```

### 3.2 Construction et lancement du stack

# Docker Compose

   ```bash
   cd src/docker
   docker compose build
   docker compose up -d
   ```

# Pipeline ETL (à la racine du projet)

   ```bash
   python3 -m etl.main --pages 10
   ```

---

## 4. Vérification des données

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

---

## 5. Kibana – Création d’une vue et d’un tableau de bord

### 5.1 Accès à Kibana

   ```bash
   Local : http://localhost:5601
   VM : http://<IP_PUBLIQUE_VM>:5601
   ```

### 5.2 Création d’une Data View

   ```bash
   Nom : NOV25_BDE_SATISFACTION_CLIENT
   Index pattern : reviews*
   Champ temporel : Aucun
   ```

### 5.3 Visualisation

1. Accéder à Elastic/Kibana depuis le navigateur : http://localhost:5601/app/home#/

2. Aller dans **Visualize Library** → **Create new visualization**

3. Sélectionner le type de visualisation : **Lens**

4. Choisir la **Data View** précédemment créée (`NOV25_BDE_SATISFACTION_CLIENT`)

5. Créer les visualisations suivantes :

   - **Histogramme des notes** (répartition des avis par score)
   - **Top catégories** (catégories les plus représentées)
   - **Volume d’avis** (nombre total d’avis ou évolution)

6. Enregistrer chaque visualisation pour pouvoir les réutiliser dans un tableau de bord.

### 5.4 Initialisation lors du premier démarrage (Docker)

⚠️ **Respecter impérativement l’ordre suivant :**

1. Lancer l’infrastructure Docker (Elasticsearch + Kibana) :

   ```bash
   cd src/docker
   docker compose up -d
   ```

2. Accéder à Elastic/Kibana :

   ```bash
   Local : http://localhost:5601/app/home#/
   VM : http://<IP_PUBLIQUE_VM>:5601/app/home#/
   ```

3. Importer les objets sauvegardés (depuis le menu hamburger) :

   - Stack Management
   - Saved Objects
   - Import
   - Sélectionner le fichier .ndjson
   - Laisser les options par défaut

4. Exécuter le pipeline ETL afin de créer et alimenter l’indice reviews :

   ```bash
   python3 -m etl.main --pages 10
   ```

5. Depuis Elastic/Kibana, aller dans Analytics :
   - Dashboards et appliquer un filtre sur les 7 derniers jours.

---

## 6. Accès à l’application Streamlit (Frontend)

   ```bash
   Local : http://localhost:8501
   VM : http://<IP_PUBLIQUE_VM>:8501
   ```

---

## 7. Tests Unitaires

### 7.1 Lancer les tests

Les tests du projet sont réalisés avec pytest.<br>
Pour exécuter tous les tests, il suffit de se rendre à la racine du projet et<br>
de lancer la commande suivante :

   ```bash
   source venv/bin/activate
   export PYTHONPATH=$(pwd)/src
   echo $PYTHONPATH
   pytest src/tests
   ```

---

## 8. Dépannage & problèmes fréquents

| Problème                           | Cause probable                                     | Solution                                                                                                                                                                                                                               |
| ---------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Elasticsearch ne démarre pas       | Port 9200 utilisé, mémoire insuffisante            | Vérifier les ports et ajuster `docker-compose.yml`                                                                                                                                                                                     |
| ConnectionError vers Elasticsearch | Service ES pas encore prêt                         | Attendre (`sleep 30`) ou ajouter un retry dans le script                                                                                                                                                                               |
| Mapping non appliqué               | Indice existant                                    | Supprimer l’indice : `DELETE /reviews`                                                                                                                                                                                                 |
| Data View introuvable              | Mauvais pattern                                    | Vérifier que le pattern est `reviews*`                                                                                                                                                                                                 |
| Problème de permissions            | Volume Docker                                      | `chmod -R 777 ./data`                                                                                                                                                                                                                  |
| Erreur Docker sous Windows         | Docker Desktop non démarré ou backend WSL2 inactif | Vérifier que **Docker Desktop** est démarré, que le backend **WSL2** est actif, puis relancer Docker Desktop. Message typique : `unable to get image docker.elastic.co/kibana/kibana:8.12.0 The system cannot find the file specified` |
