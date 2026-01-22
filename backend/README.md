# Crear imagen de docker del backend

docker build -t backend-python-api .

verificar que la imagen se creó

docker images

# Ejecutar un contenedor a partir de la imagen creada

docker run -d -p 5000:5000 -v shared:/app/shared-files --name backend-container-api  backend-python-api