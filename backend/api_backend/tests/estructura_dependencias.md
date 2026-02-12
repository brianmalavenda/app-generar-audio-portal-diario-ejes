TelegramService
    Se implementa en el inicio del proyecto
    
        from api.telegram_services import telegram_bp
        def main():
        from . import create_app
        app = create_app()
        app.register_blueprint(telegram_bp)

    Depende de una variable de entorno que proporcione el token o 
