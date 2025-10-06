#!/bin/bash
echo "🚀 Iniciando monitoreo de servicios TTS..."

# Función para mostrar logs con color
log_service() {
    local service=$1
    local color=$2
    echo -e "\n${color}=== $service ===\033[0m"
    docker logs --tail=10 -f $service &
}

# Monitorear todos los servicios
log_service "backend-container" "\033[1;34m"
log_service "api-proxy-container" "\033[1;32m" 
log_service "frontend-container" "\033[1;35m"

# Esperar Ctrl+C
echo "Presiona Ctrl+C para detener el monitoreo"
wait