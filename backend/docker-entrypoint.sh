#!/bin/bash
set -e  # Detiene el script si ocurre algún error

# Crear directorios necesarios
mkdir -p /app/shared-files/diario_pintado
mkdir -p /app/shared-files/diario_procesado
mkdir -p /app/shared-files/diario_ssml

# Ejecutar el comando pasado como argumento (en este caso, "python main.py")
exec "$@"