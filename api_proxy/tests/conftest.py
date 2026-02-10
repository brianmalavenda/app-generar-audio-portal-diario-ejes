import pytest
from unittest.mock import Mock, patch, MagicMock
import io


# @pytest.fixture
# def mock_credentials():
#     """Mock de credenciales de Google Cloud"""
#     with patch("api_proxy.gcloud_tts.client.GoogleCloudCredentials") as mock:
#         creds = Mock()
#         mock.return_value = creds
#         yield creds

@pytest.fixture
def mock_authenticator():
    """Mock del autenticador"""
    with patch("api_proxy.gcloud_tts.client.GoogleCloudAuthenticator") as mock:
        auth = Mock()
        auth.is_authenticated = True
        mock.return_value = auth
        yield auth

@pytest.fixture
def mock_tts_synthesizer():
    """Mock del sintetizador TTS"""
    with patch("api_proxy.gcloud_tts.client.TextToSpeechSynthesizer") as mock:
        synthesizer = Mock()
        
        # Simular respuesta de Google Cloud TTS
        mock_response = Mock()
        mock_response.audio_content = b"fake_audio_bytes_12345" # traduce esto a bytes reales si es necesario simulando audio
        synthesizer.synthesize.return_value = mock_response
        
        mock.return_value = synthesizer
        yield synthesizer


@pytest.fixture
def mock_gcloud_client(mock_credentials, mock_authenticator, mock_tts_synthesizer):
    """Cliente TTS con todos los mocks inyectados"""
    from api_proxy.gcloud_tts.client import GoogleCloudTTSClient
    
    client = GoogleCloudTTSClient()
    return client


# Fixtures para tests de Flask
@pytest.fixture
def app():
    """Aplicación Flask para tests"""
    from api_proxy import app  # Ajusta según tu estructura
    app.config['TESTING'] = True

    # # Configuración completa para tests
    # app.config.update({
    #     'TESTING': True,
    #     'DEBUG': False,           # Desactiva logs verbose
    #     'SERVER_NAME': 'localhost',  # Para URLs absolutas
    #     'SECRET_KEY': 'test-key',    # Para sesiones
    #     'MAX_CONTENT_LENGTH': 1024 * 1024  # Limitar tamaño archivos
    # })
    
    # # Contexto de aplicación (para usar current_app, db, etc.)
    # with app.app_context():
    #     yield app  # ← yield en lugar de return para cleanup

    return app

@pytest.fixture
def client(app):
    """Cliente de test de Flask"""
    # Setup: Crear cliente
    # testing_client = app.test_client()

    # # Contexto de la aplicación disponible durante los tests
    # ctx = app.app_context()
    # ctx.push()
    
    # yield testing_client  # Entrega el cliente al test
    
    # # Teardown: Limpiar después del test
    # ctx.pop()

    return app.test_client()


@pytest.fixture
def sample_xml():
    """XML de ejemplo para tests"""
    return """<?xml version="1.0"?>
    <speak>
        <p>Hola mundo</p>
    </speak>"""


@pytest.fixture
def mock_file_storage(sample_xml):
    """Simula un archivo subido"""
    from werkzeug.datastructures import FileStorage
    
    return FileStorage(
        stream=io.BytesIO(sample_xml.encode('utf-8')),
        filename='test.xml',
        content_type='application/xml'
    )