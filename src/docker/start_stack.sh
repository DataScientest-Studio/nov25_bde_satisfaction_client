#!/usr/bin/env bash
set -euo pipefail

# CONFIG
export AIRFLOW_UID=${AIRFLOW_UID:-$(id -u)}
COMPOSE="docker compose"
DOCKER_TIMEOUT=120

# FONCTIONS
wait_docker() {
    echo "=== Verification Docker (WSL) ==="
    echo "Assurez-vous que Docker Desktop est bien lance cote Windows"

    local elapsed=0
    local interval=5
    local max_tries=$((DOCKER_TIMEOUT / interval))
    local try=1

    until docker info >/dev/null 2>&1; do
        if [ "$try" -gt "$max_tries" ]; then
            echo "Docker n'est pas pret apres $max_tries tentatives (~${DOCKER_TIMEOUT}s)"
            exit 1
        fi

        echo "Docker non pret (tentative $try/$max_tries), attente ${interval}s..."
        sleep "$interval"

        elapsed=$((elapsed + interval))
        try=$((try + 1))
    done

    echo "Docker est pret !"
}

wait_service() {
    local name=$1
    local url=$2
    local delay=${3:-10}
    local retries=${4:-30}

    echo "=== Attente que $name soit pret ==="
    local count=0

    until curl -fs "$url" >/dev/null 2>&1; do
        count=$((count + 1))
        if [ "$count" -ge "$retries" ]; then
            echo "$name n'a pas demarre apres $((delay * retries))s"
            exit 1
        fi
        echo "$name non pret, attente ${delay}s..."
        sleep "$delay"
    done

    echo "$name pret !"
}

# VERIFICATION DOCKER
wait_docker

# NETTOYAGE COMPLET
echo "=== STOP et suppression de TOUS les containers ==="
CONTAINERS=$(docker ps -aq)
if [ -n "$CONTAINERS" ]; then
    docker stop $CONTAINERS >/dev/null
    docker rm -f $CONTAINERS >/dev/null
else
    echo "Aucun container a stopper"
fi

echo "=== Suppression des networks utilisateurs ==="
NETWORKS=$(docker network ls --format '{{.Name}}' | grep -vE '^(bridge|host|none|nat)$' || true)
for net in $NETWORKS; do
    docker network rm "$net" >/dev/null || true
done

echo "=== Suppression de TOUS les volumes ==="
VOLUMES=$(docker volume ls -q)
if [ -n "$VOLUMES" ]; then
    docker volume rm -f $VOLUMES >/dev/null
else
    echo "Aucun volume a supprimer"
fi

# BUILD & START
echo "=== Build des autres images (no-cache) ==="
$COMPOSE build --no-cache

echo "=== Initialisation Airflow ==="
$COMPOSE up -d airflow-init
while [ "$(docker inspect -f '{{.State.Running}}' airflow-init)" = "true" ]; do
    sleep 2
done

echo "=== Demarrage du stack ==="
$COMPOSE up -d

# VERIFICATION SANTE
wait_service "Elasticsearch" "http://localhost:9200"
wait_service "Kibana" "http://localhost:5601/api/status"
wait_service "Airflow Webserver" "http://localhost:8081/health"

# APRES-DEMARRAGE
echo "=== Activation DAG Airflow ==="
docker exec airflow-webserver airflow dags unpause etl_reviews_batch

echo "=== Import Kibana Saved Objects ==="
docker exec -i kibana-satisfaction \
  curl -fs -X POST \
  "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@/opt/kibana_exports/export.ndjson

echo "=== Lancement ETL manuel ==="
docker exec airflow-webserver \
  bash -c "PYTHONPATH=/opt/airflow python /opt/airflow/etl/main.py --pages 10"

# STATUS FINAL
echo ""
echo "=== Stack operationnel ==="
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
