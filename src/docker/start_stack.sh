#!/bin/bash
set -euo pipefail

export AIRFLOW_UID=${AIRFLOW_UID:-$(id -u)}
COMPOSE="docker compose"

echo "=== Vérification Docker ==="
$COMPOSE version >/dev/null

# --- Nettoyage complet Docker ---
echo "=== STOP et suppression de tous les conteneurs du stack ==="
$COMPOSE down --volumes --remove-orphans

echo "=== Suppression des images locales du stack ==="
IMAGES=("fastapi-satisfaction" "streamlit-satisfaction" "airflow-webserver" "airflow-scheduler" "airflow-init" "grafana")
for img in "${IMAGES[@]}"; do
    if docker image inspect "$img" >/dev/null 2>&1; then
        docker rmi -f "$img"
    fi
done

echo "=== Suppression des volumes Docker ==="
VOLUMES=("es-data" "grafana-data" "airflow-data" "pgdata")
for vol in "${VOLUMES[@]}"; do
    if docker volume inspect "$vol" >/dev/null 2>&1; then
        docker volume rm -f "$vol"
    fi
done

echo "=== Nettoyage système Docker complet (conteneurs, volumes, réseaux non utilisés, images orphelines) ==="
docker system prune -af --volumes

# --- Reconstruction et relance ---
echo "=== Reconstruction des images Docker (no-cache) ==="
$COMPOSE build --no-cache

echo "=== Initialisation Airflow (safe à relancer) ==="
$COMPOSE up airflow-init

echo "=== Démarrage / reprise du stack ==="
$COMPOSE up -d

# --- Attente des services ---
wait_service() {
    local name=$1
    local url=$2
    local delay=${3:-10}
    local retries=${4:-30}
    echo "=== Attente que $name soit prêt ==="
    local count=0
    until curl -s "$url" >/dev/null 2>&1; do
        count=$((count+1))
        if [ $count -ge $retries ]; then
            echo "$name n'a pas démarré après $((delay*retries)) secondes, arrêt."
            exit 1
        fi
        echo "$name non prêt, attente ${delay}s..."
        sleep $delay
    done
}

wait_service "Elasticsearch" "http://localhost:9200"
wait_service "Kibana" "http://localhost:5601/api/status"
wait_service "Airflow Webserver" "http://localhost:8081/health"

docker exec airflow-webserver airflow dags unpause etl_reviews_batch

# --- Import Kibana Saved Objects ---
echo "=== Import Kibana Saved Objects ==="
docker exec -i kibana-satisfaction \
  curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@/opt/kibana_exports/export.ndjson

# --- Lancement manuel du pipeline ETL ---
echo "=== Lancement manuel du pipeline ETL via Python ==="
docker exec airflow-webserver bash -c "PYTHONPATH=/opt/airflow python /opt/airflow/etl/main.py --pages 10"

# --- Affichage stack opérationnel ---
echo ""
echo "=== Stack opérationnel ==="
$COMPOSE ps

echo ""
echo "Airflow        : http://localhost:8081/login (admin/admin)"
echo "FastAPI        : http://localhost:8000/docs"
echo "Streamlit      : http://localhost:8501"
echo "Elasticsearch  : http://localhost:9200"
echo "Kibana         : http://localhost:5601"
echo "Grafana        : http://localhost:3000 (admin/admin)"
echo "Prometheus     : http://localhost:9090/targets"
echo "Node Exporter  : http://localhost:9100"
