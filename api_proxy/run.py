from api_proxy import create_app

def main():
    app = create_app('production')
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()