# File: src\docker\start_stack.ps1

# PowerShell script pour Windows / Docker Desktop
# Exécution dans un terminal PowerShell (admin recommandé)
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\start_stack.ps1

# CONFIG GLOBALE
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$compose = "docker-compose"
$dockerDesktopExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# FONCTIONS DOCKER
Function Start-DockerDesktop {
    Write-Output "=== Verification Docker Desktop ==="

    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker CLI introuvable. Docker Desktop est-il installe ?"
    }

    if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
        Write-Output "Docker Desktop non lance -> demarrage..."
        Start-Process $dockerDesktopExe
    } else {
        Write-Output "Docker Desktop deja lance"
    }
}

Function Wait-Docker {
    param (
        [int]$Timeout = 120
    )

    Write-Output "=== Attente du daemon Docker ==="
    $elapsed = 0

    while ($elapsed -lt $Timeout) {
        try {
            docker info *> $null
            Write-Output "Docker est pret !"
            return
        } catch {
            Write-Output "Docker non pret, attente 5s..."
            Start-Sleep -Seconds 5
            $elapsed += 5
        }
    }

    throw "Docker n'est pas pret apres $Timeout secondes"
}

Function Wait-Service {
    param (
        [string]$Name,
        [string]$Url,
        [int]$Delay = 10,
        [int]$Retries = 30
    )

    Write-Output "=== Attente que $Name soit pret ==="
    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop | Out-Null
            Write-Output "$Name pret !"
            return
        } catch {
            Write-Output "$Name non pret, attente $Delay s..."
            Start-Sleep -Seconds $Delay
        }
    }

    throw "$Name n'a pas demarre apres $($Delay * $Retries) secondes"
}

# DEMARRAGE DOCKER
Start-DockerDesktop
Wait-Docker

# NETTOYAGE COMPLET
Write-Output "=== STOP et suppression de TOUS les containers ==="
$containers = docker ps -aq
if ($containers) {
    docker stop $containers | Out-Null
    docker rm -f $containers | Out-Null
}

Write-Output "=== Suppression des networks utilisateurs ==="
$networks = docker network ls --format "{{.Name}}" |
    Where-Object { $_ -notin @("bridge","host","none","nat") }

foreach ($net in $networks) {
    docker network rm $net | Out-Null
}

Write-Output "=== Suppression de TOUS les volumes ==="
$volumes = docker volume ls -q
if ($volumes) {
    docker volume rm -f $volumes | Out-Null
}

# BUILD & START
Write-Output "=== Build des autres images (no-cache) ==="
& $compose build --no-cache

Write-Output "=== Initialisation Airflow ==="
docker compose up -d airflow-init

Write-Output "=== Attente fin airflow-init ==="
do {
    Start-Sleep -Seconds 2
    $status = docker inspect airflow-init --format '{{.State.Status}}'
    $exitCode = docker inspect airflow-init --format '{{.State.ExitCode}}'
} while ($status -eq "running")

if ($exitCode -ne 0) {
    throw "Airflow init a echoue (exit code $exitCode)"
}

Write-Output "=== Demarrage du stack ==="
& $compose up -d

# VERIFICATION SANTE
Wait-Service "Elasticsearch" "http://localhost:9200"
Wait-Service "Kibana" "http://localhost:5601/api/status"
Wait-Service "Airflow Webserver" "http://localhost:8081/health"

# APRES-DEMARRAGE
Write-Output "=== Activation DAG Airflow ==="
docker exec airflow-webserver airflow dags unpause etl_reviews_batch

Write-Output "=== Import Kibana Saved Objects ==="
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$KibanaExportDir = Join-Path $ProjectRoot "kibana_exports"
$KibanaFile = Join-Path $KibanaExportDir "export.ndjson"

if (Test-Path $KibanaFile) {
    Write-Output "Import depuis $KibanaFile"

    curl.exe -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" `
        -H "kbn-xsrf: true" `
        -F "file=@$KibanaFile" `
        --silent --show-error --fail
} else {
    Write-Warning "Aucun export Kibana trouve -> import ignore"
}

Write-Output "=== Lancement ETL manuel ==="
docker exec airflow-webserver sh -c `
  "PYTHONPATH=/opt/airflow python /opt/airflow/etl/main.py --pages 10"

# STATUS FINAL
Write-Output ""
Write-Output "=== Stack operationnel ==="
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
