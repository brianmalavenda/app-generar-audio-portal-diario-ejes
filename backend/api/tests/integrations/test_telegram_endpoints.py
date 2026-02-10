import pytest
import json
from io import BytesIO

def test_health_check(client):
    """Test del endpoint de health"""
    response = client.get('/telegram/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert "telegram" in data["services"]

def test_share_file_solo_documento(client, mock_telegram_service, sample_document_file):
    """Test compartir solo un documento"""
    # Preparar el archivo para subir
    with open(sample_document_file, 'rb') as f:
        data = {
            'file': (BytesIO(f.read()), 'documento.pdf'),
            'chat_id': '12345678',
            'caption': 'Mi documento de prueba'
        }
        
        response = client.post(
            '/telegram/share',
            data=data,
            content_type='multipart/form-data'
        )
    
    # Verificar respuesta HTTP
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["success"] is True
    assert "message_id" in result
    
    # Verificar que se llamó al servicio correctamente
    mock_telegram_service.send_document.assert_called_once()
    call_args = mock_telegram_service.send_document.call_args
    
    assert call_args[0][0] == '12345678'  # chat_id
    assert 'caption' in call_args[1] or call_args[0][2] == 'Mi documento de prueba'

def test_share_file_solo_audio(client, mock_telegram_service, sample_audio_file):
    """Test compartir solo audio"""
    with open(sample_audio_file, 'rb') as f:
        data = {
            'audio': (BytesIO(f.read()), 'audio.mp3'),
            'chat_id': '12345678',
            'title': 'Mi canción',
            'performer': 'Artista Test'
        }
        
        response = client.post(
            '/telegram/share',
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 200
    mock_telegram_service.send_audio.assert_called_once()
    
    # Verificar parámetros
    call_args = mock_telegram_service.send_audio.call_args
    assert call_args[1].get('title') == 'Mi canción'
    assert call_args[1].get('performer') == 'Artista Test'

def test_share_file_documento_y_audio(client, mock_telegram_service, 
                                      sample_document_file, sample_audio_file):
    """Test compartir ambos: documento y audio (usa send_multiple)"""
    with open(sample_document_file, 'rb') as doc, \
         open(sample_audio_file, 'rb') as audio:
        
        data = {
            'file': (BytesIO(doc.read()), 'doc.pdf'),
            'audio': (BytesIO(audio.read()), 'audio.mp3'),
            'chat_id': '12345678',
            'text': 'Aquí tienes los archivos'
        }
        
        response = client.post(
            '/telegram/share',
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 200
    
    # Debería llamar a send_multiple o ambos métodos individuales
    # dependiendo de tu implementación
    if hasattr(mock_telegram_service, 'send_multiple'):
        mock_telegram_service.send_multiple.assert_called_once()
    else:
        assert mock_telegram_service.send_document.called
        assert mock_telegram_service.send_audio.called

def test_share_file_sin_chat_id(client, mock_telegram_service, sample_document_file):
    """Test error cuando falta chat_id"""
    with open(sample_document_file, 'rb') as f:
        data = {
            'file': (BytesIO(f.read()), 'doc.pdf')
            # falta chat_id
        }
        
        response = client.post(
            '/telegram/share',
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 400
    mock_telegram_service.send_document.assert_not_called()

def test_share_file_error_telegram(client, mock_telegram_service, sample_document_file):
    """Test cuando Telegram devuelve error"""
    # Configurar mock para simular error
    mock_telegram_service.send_document.return_value = {
        "ok": False,
        "error_code": 400,
        "description": "Bad Request: chat not found"
    }
    
    with open(sample_document_file, 'rb') as f:
        data = {
            'file': (BytesIO(f.read()), 'doc.pdf'),
            'chat_id': 'chat_invalido'
        }
        
        response = client.post(
            '/telegram/share',
            data=data,
            content_type='multipart/form-data'
        )
    
    # Tu endpoint debería manejar el error y devolver 500 o 502
    assert response.status_code in [500, 502, 400]
    
    result = json.loads(response.data)
    assert "error" in result or result.get("success") is False