from api_proxy import create_app
from config import config

def main():
    app = create_app(config['development'])
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()