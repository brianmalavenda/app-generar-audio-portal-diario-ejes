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

    # Importar y registrar rutas
    from . import routes
    routes.init_routes(app)    
    return app

# Para backwards compatibility (si alguien hace "from api_proxy import app")
app = create_app()