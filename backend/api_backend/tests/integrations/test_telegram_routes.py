import pytest
from unittest.mock import patch, MagicMock

@patch('api_backend.services.client.TelegramService')
def test_share_endpoint_success(MockClient, client):
        # Configurar qué devuelve el mock
        mock_instance = MockClient.return_value
        mock_instance.send_document.return_value = {'success': True, 'message_id': 999}

        # Hacer la petición POST al endpoint
        response = client.post('/api/telegram/share', json={
            'chatId': '12345',
            'fileName': 'test.txt'
            # audioFileName es opcional
        })

        print(f"DEBUG: Respuesta del endpoint -> {response.get_json()}") # Esto saldrá en la consola
        
        # Verificar
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verificar que el endpoint llamó al método del cliente
        mock_instance.send_document.assert_called_once()

@patch('api_backend.services.client.TelegramService')
def test_healt_check_endpoint_success(MockClient, client):
        mock_instance = MockClient.return_value
        mock_instance.check_health.return_value = "PortalDiariosBot"

        response = client.get('/api/telegram/health')

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'healthy'
        assert json_data['bot_username'] == "PortalDiariosBot"

@patch('api_backend.services.routes.get_client')
def test_healt_check_endpoint_failed(MockClient,client):
    # with patch('api_backend.services.routes.get_client', return_value=None):
    MockClient.return_value = None  # Simula que no se pudo inicializar el cliente (e.g. token no configurado)
    response = client.get('/api/telegram/health')
    assert response.status_code == 503
