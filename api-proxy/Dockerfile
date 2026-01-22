FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para gcloud
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Cloud SDK
# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \
#     tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
#     curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
#     apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
#     apt-get update -y && \
#     apt-get install google-cloud-cli -y

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para caché eficiente)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Copiar el script de entrypoint para crear carpetas
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exponer puerto
EXPOSE 5000

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD ["python", "main.py"]