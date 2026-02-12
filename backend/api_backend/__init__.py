from flask import Flask
from flask_cors import CORS
import os


def create_app(config_name='development'):
    # load_dotenv()
    
    app = Flask(__name__)
    
    # Configuración
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost']
    CORS(app, origins=ALLOWED_ORIGINS)
    
    # Configuraciones por entorno
    app.config['TESTING'] = (config_name == 'testing')
    app.config['DEBUG'] = (config_name == 'development')
    app.config['PRODUCTION'] = (config_name == 'production')
    app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', '/app/shared-files/audio/')
    app.config['SAVE_FOLDER'] = os.path.join(os.getcwd(), "shared-files", "diario_pintado")  # ruta absoluta dentro del contenedor

    # Registrar blueprints de rutas
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Registrar blueprint de Telegram
    from services.telegram import telegram_bp
    app.register_blueprint(telegram_bp)

    return app

# Para backwards compatibility (si alguien hace "from api_proxy import app")
app = create_app()