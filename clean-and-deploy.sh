#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    echo -e "${2}${1}${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar que estamos en el directorio correcto
check_directory() {
    if [[ ! -f "docker-compose.yml" ]]; then
        print_color "Error: No se encuentra docker-compose.yml en el directorio actual" "$RED"
        print_color "Ejecuta este script desde la raíz de tu proyecto" "$YELLOW"
        exit 1
    fi
}

# Limpiar servicios de Docker Swarm
clean_swarm() {
    print_color "=== Limpiando Docker Swarm ===" "$BLUE"
    
    if docker stack ls | grep -q "mi-app"; then
        print_color "Eliminando stack mi-app..." "$YELLOW"
        docker stack rm mi-app
        sleep 10
    else
        print_color "No se encontró stack mi-app" "$GREEN"
    fi
    
    # Eliminar servicios individuales por si existen
    for service in mi-app_frontend mi-app_backend mi-app_api-proxy; do
        if docker service ls | grep -q "$service"; then
            print_color "Eliminando servicio $service..." "$YELLOW"
            docker service rm "$service"
            sleep 5
        fi
    done
}

# Limpiar contenedores
clean_containers() {
    print_color "=== Limpiando contenedores ===" "$BLUE"
    
    # Detener y eliminar contenedores relacionados con la app
    print_color "Deteniendo contenedores..." "$YELLOW"
    docker stop $(docker ps -aq --filter "name=api-proxy-container") 2>/dev/null || true
    docker stop $(docker ps -aq --filter "name=backend-container") 2>/dev/null || true
    docker stop $(docker ps -aq --filter "name=frontend-container") 2>/dev/null || true
    
    print_color "Eliminando contenedores..." "$YELLOW"
    docker rm $(docker ps -aq --filter "name=api-proxy-container") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=backend-container") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=frontend-container") 2>/dev/null || true
    
    # Eliminar todos los contenedores detenidos
    docker container prune -f
}

# Limpiar imágenes
clean_images() {
    print_color "=== Limpiando imágenes ===" "$BLUE"
    
    # Eliminar imágenes dangling (sin tag)
    print_color "Eliminando imágenes huérfanas..." "$YELLOW"
    docker image prune -f
    
    # Opcional: eliminar imágenes específicas de la app
    read -p "¿Deseas eliminar las imágenes de la aplicación? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_color "Eliminando imágenes de la aplicación..." "$YELLOW"
        docker rmi api-proxy:latest 2>/dev/null || true
        docker rmi backend:latest 2>/dev/null || true
        docker rmi frontend:latest 2>/dev/null || true
    fi
}

# Limpiar redes
clean_networks() {
    print_color "=== Limpiando redes ===" "$BLUE"
    
    # Eliminar redes no utilizadas
    docker network prune -f
    
    # Eliminar red específica si existe
    if docker network ls | grep -q "tts-network"; then
        print_color "Eliminando red tts-network..." "$YELLOW"
        docker network rm tts-network
    fi
}

# Limpiar volúmenes
clean_volumes() {
    print_color "=== Limpiando volúmenes ===" "$BLUE"
    
    # Preguntar si eliminar volúmenes (pueden contener datos importantes)
    read -p "¿Deseas eliminar los volúmenes? Esto borrará todos los datos persistentes (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_color "Eliminando volúmenes no utilizados..." "$YELLOW"
        docker volume prune -f
    else
        print_color "Manteniendo volúmenes (datos persistentes)" "$GREEN"
    fi
}

# Reconstruir imágenes
rebuild_images() {
    print_color "=== Reconstruyendo imágenes ===" "$BLUE"
    
    if [[ -d "api-proxy" ]]; then
        print_color "Construyendo api-proxy..." "$YELLOW"
        docker build -t api-proxy:latest ./api-proxy
    fi
    
    if [[ -d "backend" ]]; then
        print_color "Construyendo backend..." "$YELLOW"
        docker build -t backend:latest ./backend
    fi
    
    if [[ -d "frontend" ]]; then
        print_color "Construyendo frontend..." "$YELLOW"
        docker build -t frontend:latest ./frontend
    fi
}

# Verificar estado del sistema
check_system() {
    print_color "=== Estado del sistema ===" "$BLUE"
    
    print_color "Contenedores activos:" "$YELLOW"
    docker ps
    
    print_color "Servicios activos:" "$YELLOW"
    docker service ls
    
    print_color "Redes:" "$YELLOW"
    docker network ls
    
    print_color "Imágenes:" "$YELLOW"
    docker images | grep -E "(api-proxy|backend|frontend)"
}

# Desplegar con docker-compose
deploy_compose() {
    print_color "=== Desplegando con Docker Compose ===" "$BLUE"
    
    print_color "Ejecutando docker-compose up..." "$YELLOW"
    docker-compose up -d
    # docker stack deploy -c docker-compose.yml mi-app
    
    print_color "Esperando que los servicios inicien..." "$YELLOW"
    sleep 10
    
    print_color "Estado de los contenedores:" "$YELLOW"
    docker-compose ps
}

# Probar servicios
test_services() {
    print_color "=== Probando servicios ===" "$BLUE"
    
    print_color "Probando backend (puerto 5000)..." "$YELLOW"
    curl -f http://127.0.0.1:5000/api/health || print_color "Backend no responde" "$RED"
    
    print_color "Probando api-proxy (puerto 5001)..." "$YELLOW"
    curl -f http://127.0.0.1:5001/api_proxy/health || print_color "API Proxy no responde" "$RED"
    
    print_color "Probando frontend (puerto 3000)..." "$YELLOW"
    curl -f http://127.0.0.1:3000 || print_color "Frontend no responde" "$RED"
}

# Menú principal
main() {
    print_color "=== Limpiador y Desplegador de Microservicios TTS ===" "$BLUE"
    
    check_directory
    
    # Mostrar opciones
    echo "Opciones:"
    echo "1) Limpieza completa + Deploy"
    echo "2) Solo limpieza"
    echo "3) Solo deploy"
    echo "4) Solo test"
    echo "5) Estado actual"
    read -p "Selecciona una opción (1-5): " option
    
    case $option in
        1)
            clean_swarm
            clean_containers
            clean_networks
            clean_volumes
            clean_images
            rebuild_images
            deploy_compose
            test_services
            ;;
        2)
            clean_swarm
            clean_containers
            clean_networks
            clean_volumes
            clean_images
            ;;
        3)
            rebuild_images
            deploy_compose
            test_services
            ;;
        4)
            test_services
            ;;
        5)
            check_system
            ;;
        *)
            print_color "Opción inválida" "$RED"
            exit 1
            ;;
    esac
    
    print_color "=== Proceso completado ===" "$GREEN"
}

# Ejecutar menú principal
main