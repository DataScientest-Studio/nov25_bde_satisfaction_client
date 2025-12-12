# NOV25 BDE Satisfaction Client - Pipeline ETL

Ce dépôt contient un pipeline d'Extract‑Transform‑Load (ETL) qui récupère les avis publiés sur [Trustpilot](https://fr.trustpilot.com/) et les indexe dans Elasticsearch sous le nom d’indice reviews.

Le projet peut être exécuté :

Mode                          | Avantages
----------------------------- | -----------------------------------------------------------
Localement (sans Docker)      | Débogage rapide, pas besoin de services externes.
Docker‑Compose                 | Isolation des dépendances, idéal pour CI/CD ou mise en prod.

⚠️ Important - Si vous lancez le pipeline localement, commentez la partie « Chargement dans Elasticsearch » dans etl/etl_reviews.py.

Le runtime local ne démarre pas d’Elasticsearch par défaut.

Table des matières
1. Prérequis
2. Configuration et exécution locale
3. Exécution avec Docker Compose
    - 3.1. Nettoyage de l’environnement
    - 3.2. Construction et lancement du stack
4. Vérification des données
5. Kibana - Création d’une vue et d’un tableau de bord
6. Dépannage & problèmes fréquents

---

1  Prérequis
Outil                            | Version minimale | Installation ?
-------------------------------- | ---------------- | --------------
Python                           | 3.10+            | ✅ (pip, venv)
Docker                           | 20.x+            | ✅
docker‑compose                   | 1.29+            | ✅
ElasticSearch (si vous voulez l’exécuter localement) | 8.12+ | optionnel
Kibana (pour la visualisation)   | 8.12+            | optionnel

Remarque : Pour tester uniquement la logique ETL, il suffit d’installer Python et les dépendances du requirements.txt.

Les scripts de chargement dans Elasticsearch sont désactivés par défaut.

---

2  Configuration et exécution locale
Créer l’environnement virtuel
python -m venv venv

Activer l’environnement
macOS / Linux :
source venv/bin/activate

Windows PowerShell :
.\venv\Scripts\activate

Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

Lancer le pipeline (10 pages)
python main.py --pages 10

🔧 Astuce : Si vous ne voulez pas charger les données dans Elasticsearch localement, ouvrez etl/etl_reviews.py et commentez la section :

```python
# # Chargement Elasticsearch
# es = Elasticsearch(hosts=["localhost:9200"])
# ...
```
---

3  Exécution avec Docker Compose

3.1 Nettoyage complet (si besoin)
Ces commandes suppriment les conteneurs, images et volumes inutilisés pour repartir d’un état propre.

Arrêter / Supprimer tous les conteneurs
docker ps -a -q | xargs -r docker stop
docker ps -a -q | xargs -r docker rm

Supprimer toutes les images (optionnel, à faire avec prudence)
docker images -q | xargs -r docker rmi -f

Supprimer tous les volumes Docker
docker volume ls -q | xargs -r docker volume rm

Nettoyer le répertoire de données (si présent)
docker compose down -v
rm -rf ./data/*
mkdir -p ./data
chmod -R 777 ./data
Attention : Les commandes ci‑dessus suppriment tous les volumes et images Docker.
Utilisez‑les uniquement si vous êtes sûr de ne pas garder d’autres conteneurs actifs.

3.2 Construction et lancement du stack
Construire l’image app
docker compose build app

Lancer les services en arrière-plan (Elasticsearch + Kibana)
docker compose up -d

Exécuter le pipeline une seule fois (en mode interactif)
docker compose run --rm app python main.py --pages 10

Vérifier que l’indice a bien été créé
curl -s -X GET "http://localhost:9200/reviews/_mapping?pretty"
Vous devriez voir la définition du mapping de reviews.

---

4  Vérification des données

Mapping :
curl http://localhost:9200/reviews/_mapping

Recherche simple (exemple) :
curl -X GET "http://localhost:9200/reviews/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} }
}'

---

5  Kibana - Création d’une vue et d’un tableau de bord
Accéder à Kibana
http://<IP_PUBLIQUE_VM>:5601/app/home#/
OU
http://localhost:5601/app/home#/

Créer une Data View
Nom : NOV25_BDE_SATISFACTION_CLIENT
Pattern d’index : reviews*
Timestamp field : Aucun (vous ne voulez pas filtrer par temps)

Visualiser les données
Aller dans Visualize Library → Create new visualization → Lens
Sélectionner la Data View créée ci‑dessus
Créer des graphiques (par exemple histogramme de note, top 10 catégories, etc.)
(Optionnel) Exporter ou partager le tableau de bord via Share → Permalink.

---

6  Dépannage & problèmes fréquents

Problème                                   | Cause probable                                                | Solution
------------------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------
Elasticsearch ne démarre pas               | Port déjà utilisé, mémoire insuffisante, paramètres de JVM trop élevés | Vérifier le port (9200) et ajuster la configuration Docker (docker-compose.yml) ou augmenter les ressources allouées.
Erreur ConnectionError vers Elasticsearch | Service ES n’est pas encore prêt lors du lancement du pipeline | Ajouter un délai ou une logique retry dans le script, ou démarrer le pipeline après que docker compose up -d ait fini de lancer tous les conteneurs (sleep 30).
Mapping non appliqué                       | Le script ne recrée pas l’indice à chaque exécution           | Nettoyer l’indice avant de relancer (curl -X DELETE http://localhost:9200/reviews) ou utiliser es.indices.create(index='reviews', body={...}) dans le pipeline.
Kibana "Data view not found"               | Le pattern d’index est incorrect, l’indice n’existe pas       | Vérifier que l’indice reviews existe (curl http://localhost:9200/_cat/indices) et que le pattern reviews* correspond.
Permissions sur le répertoire data      | Docker ne peut pas écrire dans le volume partagé              | Donner les droits 777 ou configurer un utilisateur UID/GID cohérent dans Dockerfile (ex. RUN useradd -u 1000 app && chown -R app:app /data).
