from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import os
from .repositories.file_repository import FileRepository

def create_app(config_name='development'):
    # load_dotenv()
    
    app = Flask(__name__)
    
    # Configuración
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost']
    CORS(app, origins=ALLOWED_ORIGINS)
    
    # Configuraciones por entorno
    app.config['TESTING'] = (config_name == 'testing')
    if config_name == 'testing':
        app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', '/tests/files/audio/')
        app.config['SAVE_FOLDER'] = os.getenv('SAVE_FOLDER', '/tests/files/diario_pintado/')

    app.config['DEBUG'] = (config_name == 'development')
    app.config['PRODUCTION'] = (config_name == 'production')
    app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', '/shared-files/audio/')
    app.config['SAVE_FOLDER'] = os.getenv('SAVE_FOLDER', (os.path.join(os.getcwd(), "shared-files", "diario_pintado")))  # ruta absoluta dentro del contenedord
    
    app.config['DB_CONFIG'] = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'ejes_db'),
        'pool_name': "mypool_connection",
        'pool_size': 5
    }

    app.file_repository = FileRepository(app.config['DB_CONFIG'])

    # app.secret_key = os.getenv('SECRET_KEY', os.getenv('SECRET_KEY_APP', 'unaclavecualquiera'))

    # Registrar blueprints de rutas
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Registrar blueprint de Telegram
    from .services import telegram_bp
    app.register_blueprint(telegram_bp)

    return app

# Para backwards compatibility (si alguien hace "from api_backend import app")
# app = create_app()