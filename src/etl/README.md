# NOV25_BDE_SATISFACTION_CLIENT

## Lancement ETL local (sans Docker) :

python -m venv venv
pip install -r requirements.txt
source venv/bin/activate
### Il faut commenter la partie "Chargement Elasticsearch" dans etl_project/etl/etl_reviews.py
python main.py --pages 10

## Lancement ETL via Docker Compose (manuel, sans démarrer toute la stack)

### Nettoyage si nécessaire :

docker ps -a -q
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker images -q
docker rmi -f $(docker images -q)
docker volume ls -q
docker volume rm $(docker volume ls -q)

docker compose down -v
rm -rf ./datas/*
mkdir -p ./datas
chmod -R 777 ./datas
sudo rm -rf data/elasticsearch/*
sudo rm -rf ./data/elasticsearch
sudo mkdir -p ./data/elasticsearch
sudo chown -R 1000:1000 ./data/elasticsearch
sudo chmod -R 775 ./data/elasticsearch

### Construction et exécution :

docker compose build app
docker compose up -d
docker compose run --rm app python main.py --pages 10

curl -s -X GET "http://localhost:9200/reviews/_mapping?pretty"

### Accès à ElasticSearch/Kibana depuis le navigateur :

http://IP_PUBLIQUE_VM:5601/app/home#/

GET /reviews/_mapping
GET /reviews/_search

### Créer un vue depuis Kibana
- Create data view
 -> Name : NOV25_BDE_SATISFACTION_CLIENT
 -> Index pattern : reviews*
 -> Timestamp field : I don’t want to use the time filter
- Visualize Library
 -> Create new visualization
 -> Lens

### Depuis la VM :

mkdir -p datas
chmod -R 777 datas

tar -cvf etl_$(date +%Y%m%d%H%M%S).tar \
config \
datas \
pipeline \
extract \
load \
transform \
utils \
.dockerignore \
docker-compose.yml \
Dockerfile \
main.py \
README.md \
requirements.txt
