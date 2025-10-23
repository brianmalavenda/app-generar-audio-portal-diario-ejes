#!/bin/bash
set -e

# Crear directorios necesarios en el volumen compartido
mkdir -p /app/shared-files/diario_pintado
mkdir -p /app/shared-files/diario_procesado
mkdir -p /app/shared-files/diario_ssml
mkdir -p /app/shared-files/audio
mkdir -p /app/shared-files/audio/optimizado

# Verificar que los directorios se crearon
echo "Directorios creados en: /app/shared-files/"
ls -la /app/shared-files/

# Ejecutar el comando principal
exec "$@"