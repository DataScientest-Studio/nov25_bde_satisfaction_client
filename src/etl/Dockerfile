# File: Dockerfile

FROM python:3.11-slim

# Evite que les logs soient bufferisés
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copier et installer les dépendances avec version compatible Elasticsearch 8.x
COPY requirements.txt .

# Mettre à jour pip puis installer les dépendances
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Crée le dossier data et donne les permissions
RUN mkdir -p /app/data && chmod -R 777 /app/data

# Copier tout le code
COPY . .
