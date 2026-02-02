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
COPY . .

# Instalar el paquete en modo editable
RUN pip install --no-cache-dir .

# Crear directorios necesarios
RUN mkdir -p /app/shared-files /app/secrets && \
    chmod 700 /app/secrets

# Variable de entorno para credenciales
ARG GOOGLE_CREDENTIALS=/app/secrets/google-credentials.json
ENV GOOGLE_CREDENTIALS=${GOOGLE_CREDENTIALS}

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