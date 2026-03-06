from flask import Flask
from api_backend import create_app

# Crear la app a nivel de módulo para que Gunicorn la encuentre
app = create_app()

def main():
    app.run(host='0.0.0.0', port=5000)  # Cambiar localhost a 0.0.0.0

if __name__ == '__main__':
    main()