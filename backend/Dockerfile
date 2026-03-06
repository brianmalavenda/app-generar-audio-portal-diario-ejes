# Dockerfile
FROM python:3.11-slim

# 1. Instalar FFmpeg y dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
# Limpiar caché para reducir tamaño de la imagen
    
# Directorio de trabajo
WORKDIR /app

# Copiar archivos de definición de paquete
COPY pyproject.toml README.md ./

RUN pip install -e .

COPY api_backend/ ./api_backend/
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Instalar dependencias usando pyproject.toml
# --no-deps no es necesario aquí, pero .[dev] instalaría deps de desarrollo si quisieras
# RUN pip uninstall api_proxy -y 2>/dev/null && pip install --no-cache-dir -e . 2>/dev/null

# Copiar el script de entrypoint para crear carpetas
# COPY docker-entrypoint.sh .
# RUN chmod +x docker-entrypoint.sh
# el volumen lo tengo que crear en el momento de correr el contenedor

# Exponer puerto (FastAPI por defecto en 5000)
EXPOSE 5000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
# Usar Gunicorn (Producción) en lugar de python main.py
# Asumiendo que creaste un punto de entrada wsgi.py o usando el módulo
# CMD ["python", "-m", "api_backend"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "api_backend.__main__:app"]
# CMD ["api_backend"]
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "__main__:app"]