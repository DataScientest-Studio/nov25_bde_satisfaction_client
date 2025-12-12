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

# Crée le dossier datas et donne les permissions
RUN mkdir -p /app/datas && chmod -R 777 /app/datas

# Copier tout le code
COPY . .
