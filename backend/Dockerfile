# Dockerfile
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para caché eficiente)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# Copiar el script de entrypoint para crear carpetas
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
# el volumen lo tengo que crear en el momento de correr el contenedor

# Exponer puerto (FastAPI por defecto en 5000)
EXPOSE 5000

# Comando para ejecutar la app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD ["python", "main.py"]