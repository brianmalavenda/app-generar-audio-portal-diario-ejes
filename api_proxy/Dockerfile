FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    gcc \
    curl \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar TODO el proyecto primero (necesario para pip install -e .)
# COPY . .
COPY pyproject.toml README.md ./
COPY api_proxy/ ./api_proxy/
COPY secrets/ ./secrets/

# Instalar el paquete en modo editable para que los cambios se reflejen inmediatamente
# RUN pip install --no-cache-dir -e . 
RUN pip uninstall api_proxy -y 2>/dev/null && \
   pip install --no-cache-dir -e . 2>/dev/null

# Crear directorios necesarios
# RUN mkdir -p /app/shared-files /app/secrets && \
RUN mkdir -p /app/shared-files && \
    chmod 700 /app/secrets && \
    chmod 600 /app/secrets/* && \
    chmod 644 /app/secrets/gcloud_credentials.json

# Variable de entorno para credenciales
ARG GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcloud_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/secrets

USER appuser

EXPOSE 5000

# Ejecutar usando el entry point del paquete instalado
# CMD ["python", "-m", "api_proxy"]
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["api-proxy"]