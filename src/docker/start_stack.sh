#!/bin/bash
set -euo pipefail

export AIRFLOW_UID=${AIRFLOW_UID:-$(id -u)}
COMPOSE="docker compose"

echo "=== Vérification Docker ==="
$COMPOSE version >/dev/null

echo "=== Initialisation Airflow (safe à relancer) ==="
$COMPOSE up airflow-init

echo "=== Démarrage / reprise du stack ==="
$COMPOSE up -d

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
