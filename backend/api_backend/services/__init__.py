from .routes import telegram_bp
# from .client import TelegramService

# Expongo el blueprint para que puede ser accedido desde __init__.py de api_backend
__all__ = ['telegram_bp']