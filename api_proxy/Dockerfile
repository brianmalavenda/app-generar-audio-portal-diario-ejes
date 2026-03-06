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

RUN pip install -e .

COPY api_proxy/ ./api_proxy/
COPY secrets/ ./secrets/

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Instalar el paquete en modo editable para que los cambios se reflejen inmediatamente
# RUN pip install --no-cache-dir -e . 
# RUN pip uninstall api_proxy -y 2>/dev/null && pip install --no-cache-dir -e . 2>/dev/null

# Crear directorios necesarios
# RUN mkdir -p /app/shared-files /app/secrets && \
# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/secrets

USER appuser

EXPOSE 5000

# Ejecutar usando el entry point del paquete instalado

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "api_proxy.__main__:app"]
# CMD ["python", "-m", "api_proxy"]
# CMD ["api_proxy"]
# requiere que este instalado el paquete api_proxy, lo cual se hace con pip install -e . en el Dockerfile, pero eso no funciona bien con el volumen montado, porque el código del host sobrescribe el código del contenedor, y si el paquete no estaba instalado previamente, no encuentra el módulo api_proxy. Por eso es mejor usar python -m api_proxy, que busca el módulo en el PYTHONPATH, que incluye el directorio actual.