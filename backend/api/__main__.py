from flask import Flask
from api.telegram_services import telegram_bp

def main():
    from . import create_app
    app = create_app()
    app.register_blueprint(telegram_bp)
    app.run(host='localhost', port=5000)    

if __name__ == '__main__':
    main()