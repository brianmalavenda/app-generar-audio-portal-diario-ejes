
@pytest.fixture
def mock_telegram_service():
    """
    Mock de la instancia de TelegramService.
    Devuelve un mock listo para inyectar en los endpoints.
    """
    mock = Mock()
    
    # Respuestas realistas de la API de Telegram
    mock.send_document.return_value = {
        "ok": True,
        "result": {
            "message_id": 12345,
            "chat": {"id": 67890, "type": "private"},
            "date": 1699999999
        }
    }
    
    mock.send_audio.return_value = {
        "ok": True,
        "result": {
            "message_id": 12346,
            "chat": {"id": 67890},
            "audio": {"file_id": "audio_123", "duration": 120}
        }
    }
    
    mock.send_multiple.return_value = {
        "document_sent": True,
        "audio_sent": True,
        "message_ids": [12345, 12346]
    }
    
    return mock

@pytest.fixture
def mock_telegram_client():
    """Cliente Telegram"""
    from api.services.telegram import TelegramService
    
    client = TelegramService(token="fake_token")
    return client

@pytest.fixture
def app(mock_telegram_service, mock_telegram_env):
    """
    Crea la app de Flask con el servicio mockeado.
    ESTA es la clave: inyectás el mock antes de importar los blueprints.
    """
    # Opción 1: Si tu app permite inyección (mejor)
    from api.app import create_app
    app = create_app(telegram_service=mock_telegram_service)
    
    # Opción 2: Si no permitís inyección, parcheás el módulo
    # with patch("api.routes.telegram.telegram_service", mock_telegram_service):
    #     from api.app import create_app
    #     app = create_app()
    
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """Cliente de test para hacer requests"""
    return app.test_client()

# Fixtures para tests de Flask
@pytest.fixture
def app():
    """Aplicación Flask para tests"""
    from api_proxy import app  # Ajusta según tu estructura
    app.config['TESTING'] = True
    return app