# Mezcla de patrones de registro de rutas:
Tienes una mezcla confusa entre el uso de Blueprints (moderno y escalable) y el registro manual de rutas mediante funciones (init_routes).
En telegram.py usas Blueprint (correcto).
En routes.py usas una función init_routes(app) que decora rutas sobre la instancia app global (anticuado y propenso a ciclos de importación).
Solución: Convierte routes.py en un Blueprint más. Esto hace que tu app sea modular y fácil de escalar.

# Inicialización de Servicios (Global vs App Context):
En telegram.py, instancias la clase TelegramService a nivel global:
python

telegram_service = TelegramService() # Se ejecuta al importar el archivo
Esto es arriesgado. Si la variable de entorno TELEGRAM_BOT_TOKEN no está cargada en el momento exacto de la importación, la aplicación crashearé antes de siquiera iniciar. Además, dificulta los tests (no puedes mockear fácilmente el servicio).
Solución: Inicializa el servicio dentro de la función que crea la app o usa current_app dentro del contexto de la petición.

# Comando de ejecución:
Usas CMD ["python", "main.py"].
No veo el archivo main.py en la raíz del código que enviaste. Veo api/__main__.py. Si el archivo no existe, el contenedor fallará.
Para un contenedor Docker, siempre es mejor usar un servidor WSGI de producción (Gunicorn) en lugar del servidor de desarrollo de Flask (app.run). Tienes gunicorn en las dependencias, úsalo en el CMD.