# Nombre del servicio: api-proxy
---
📁 Estructura de archivos:
  📁 gcloud_CLI/
  📁 test/
  📁 utils/
  📄 .gitignore
  📄 docker-entrypoint.sh
  📄 gcloud_SA_access.py
  📄 requirements.txt
  📄 Dockerfile
  📄 main.py
  📄 utils.py
  📄 .env
  📄 README.md

## Principales responsabilidades:
- Autenticarse con Google Cloud
- Sintetizar el audio con la api text-to-speech de Google Cloud

## Endpoints principales:
- GET /api_proxy/health
- GET /api_proxy/generar_audio
- GET /api_proxy/sintetizar_audio
- POST /api/usuarios
- [etc.]

## Dependencias externas:
- Base de datos: -
- Servicios que consume: [gcloud]
- Servicios que lo consumen: [backend]

## Arquitectura de Comunicación

- Patrones de comunicación entre servicios (REST/gRPC/Eventos)
- Si usas message broker (Kafka/RabbitMQ/etc.)
- Cómo manejan la autenticación/autorización
- Cómo gestionan la configuración distribuida

## Estructura compartida
- ¿Tienen bibliotecas compartidas?
- ¿Cómo manejan DTOs/entidades comunes?
- ¿Tienen contratos de API compartidos?