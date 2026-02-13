import os
import pytest
from unittest.mock import patch, MagicMock
from api_backend.services.client import TelegramService

@pytest.fixture
def telegram_service():
    return TelegramService(token="fake_test_token")

def test_send_document_success(telegram_service, tmp_path):
    """Verifica que se envía un documento correctamente"""
    
    # 1. Crear un archivo falso temporal para la prueba
    dummy_file = tmp_path / "test.txt"
    dummy_file.write_text("contenido de prueba")

    # 2. Simular (Mockear) la llamada HTTP
    with patch.object(telegram_service.session, 'post') as mock_post:
        # Configurar la respuesta simulada de Telegram
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"message_id": 123, "document": {"file_name": "test.txt"}, "success": True}}

        mock_post.return_value = mock_response

        # 3. Ejecutar el método
        result = telegram_service.send_document("chat_id_123", str(dummy_file))

        # 4. Verificar resultados
        assert result['success'] is True
        assert result['message_id'] == 123

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "sendDocument" in args[0]
        assert kwargs['data']['chat_id'] == "chat_id_123"

def test_send_document_file_not_found(telegram_service):
    # Configuramos el escenario
    ruta_falsa = "/ruta/que/no/existe.txt"
        
    # "Espero que dentro de este bloque se lance un FileNotFoundError"
    with pytest.raises(FileNotFoundError):
        # Esta línea intenta abrir el archivo, falla, y lanza la excepción
        telegram_service.send_document("chat_id", ruta_falsa)