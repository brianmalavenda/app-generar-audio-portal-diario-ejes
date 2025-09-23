#!/bin/bash
# deploy.sh

echo "Construyendo imágenes..."
docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker build -t api-proxy:latest ./api-proxy

# 1. Inicializar swarm (si no está inicializado)
if ! docker node ls > /dev/null 2>&1; then
    echo "Inicializando Docker Swarm..."
    docker swarm init
fi

# 2. Crear secret (si no existe)
if ! docker secret ls | grep -q google_credentials; then
    echo "Creando secret google_credentials..."
    docker secret create google_credentials ./cred/google-credentials.json
fi

# 3. Desplegar stack
echo "Desplegando aplicación..."
docker stack deploy -c docker-compose.yml tu-app