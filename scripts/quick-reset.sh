#!/bin/bash
echo "=== Limpieza rápida ==="
docker stack rm mi-app 2>/dev/null
docker-compose down
docker system prune -f
docker-compose up -d --build
echo "=== Listo! ==="