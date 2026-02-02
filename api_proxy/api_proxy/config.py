import os

class Config:
    """Configuración base"""
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS', '/app/secrets/google-credentials.json') # ruta por defecto en contenedor
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}