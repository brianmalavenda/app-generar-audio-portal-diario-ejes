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

# Crear directorio para archivos
RUN mkdir -p /shared-files/diario_pintado
# Crear directorio para archivos
RUN mkdir -p /shared-files/diario_procesado
# Crear directorio para archivos
RUN mkdir -p /shared-files/diario_ssml

# Exponer puerto (FastAPI por defecto en 5000)
EXPOSE 5000

# Comando para ejecutar la app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
CMD ["python", "main.py"]