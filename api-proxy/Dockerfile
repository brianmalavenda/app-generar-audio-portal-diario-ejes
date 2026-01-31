FROM python:3.11-slim

# Instalar dependencias del sistema si es necesario
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copiar el paquete primero
COPY gcloud_tts/ ./gcloud_tts/

# 2. Instalar el paquete en modo desarrollo
RUN pip install -e ./gcloud_tts/

# 3. Copiar requirements e instalar dependencias de la app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY main.py .

# Crear directorios necesarios
RUN mkdir -p /app/shared-files

# Crear directorio para credenciales (vacío en la imagen)
RUN mkdir -p /app/secrets && chmod 700 /app/secrets

# Variable de entorno (apunta a donde MONTAREMOS las credenciales)
ENV GOOGLE_CREDENTIALS=/app/secrets/google-credentials.json

EXPOSE 5000

# Usuario no-root (seguridad)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app \
    # Asegurar que el directorio de credenciales tenga permisos
    chmod 755 /app/secrets
USER appuser

EXPOSE 5000

CMD ["python", "main.py"]