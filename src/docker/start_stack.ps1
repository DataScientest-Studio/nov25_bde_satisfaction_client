# File: start_stack.ps1
# PowerShell script pour Windows / Docker Desktop
# Execution dans un terminal PowerShell en mode administrateur
# $ Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# $ .\start_stack.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Variables Docker Compose
$compose = "docker-compose"

# --- Nettoyage complet Docker ---
Write-Output "=== STOP et suppression de tous les conteneurs du stack ==="
& $compose down --volumes --remove-orphans

# Suppression des images locales
$images = @(
    "fastapi-satisfaction",
    "streamlit-satisfaction",
    "airflow-webserver",
    "airflow-scheduler",
    "airflow-init",
    "grafana"
    )
foreach ($img in $images) {
    try {
        docker image inspect $img *> $null
        Write-Output "Suppression de l'image $img"
        docker rmi -f $img
    }
    catch {
        Write-Output "Image $img inexistante, skip"
    }
}

# Suppression des volumes
$volumes = @(
    "es-data",
    "grafana-data",
    "airflow-data",
    "pgdata"
)
foreach ($vol in $volumes) {
    try {
        docker volume inspect $vol *> $null
        Write-Output "Suppression du volume $vol"
        docker volume rm -f $vol
    }
    catch {
        Write-Output "Volume $vol inexistant, skip"
    }
}

Write-Output "=== Nettoyage système Docker complet ==="
docker system prune -af --volumes

# --- Reconstruction et relance ---
Write-Output "=== Reconstruction des images Docker (no-cache) ==="
& $compose build --no-cache

Write-Output "=== Initialisation Airflow ==="
& $compose up airflow-init

Write-Output "=== Démarrage / reprise du stack ==="
& $compose up -d

# --- Fonction pour attendre qu'un service soit prêt ---
Function Wait-Service {
    param (
        [string]$Name,
        [string]$Url,
        [int]$Delay=10,
        [int]$Retries=30
    )
    Write-Output "=== Attente que $Name soit prêt ==="
    for ($i=0; $i -lt $Retries; $i++) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop | Out-Null
            Write-Output "$Name prêt !"
            return
        } catch {
            Write-Output "$Name non prêt, attente $Delay s..."
            Start-Sleep -Seconds $Delay
        }
    }
    throw "$Name n'a pas démarré après $($Delay*$Retries) secondes"
}

# --- Attente des services ---
Wait-Service "Elasticsearch" "http://localhost:9200"
Wait-Service "Kibana" "http://localhost:5601/api/status"
Wait-Service "Airflow Webserver" "http://localhost:8081/health"

# --- Import Kibana Saved Objects ---
Write-Output "=== Import Kibana Saved Objects ==="
$kibanaFile = "C:\path\to\kibana_exports\export.ndjson"
docker exec -i kibana-satisfaction powershell -Command `
    "Invoke-WebRequest -Uri 'http://localhost:5601/api/saved_objects/_import?overwrite=true' -Method POST -Headers @{ 'kbn-xsrf'='true' } -InFile '$kibanaFile'"

# --- Lancement manuel du pipeline ETL ---
Write-Output "=== Lancement manuel du pipeline ETL via Python ==="
docker exec airflow-webserver powershell -Command `
    "PYTHONPATH=/opt/airflow python /opt/airflow/etl/main.py --pages 10"

# --- Affichage stack opérationnel ---
Write-Output ""
Write-Output "=== Stack opérationnel ==="
& $compose ps

Write-Output ""
Write-Output "Airflow        : http://localhost:8081/login (admin/admin)"
Write-Output "FastAPI        : http://localhost:8000/docs"
Write-Output "Streamlit      : http://localhost:8501"
Write-Output "Elasticsearch  : http://localhost:9200"
Write-Output "Kibana         : http://localhost:5601"
Write-Output "Grafana        : http://localhost:3000 (admin/admin)"
Write-Output "Prometheus     : http://localhost:9090/targets"
Write-Output "Node Exporter  : http://localhost:9100"
