import pytest
from unittest.mock import Mock, patch, MagicMock
import io
import json


class TestGenerarAudioEndpoint:
    """Tests del endpoint /api_proxy/generar_audio"""
    
    def test_missing_file_returns_400(self, client):
        """Error cuando no se envía archivo"""
        # Act
        response = client.post('/api_proxy/generar_audio')
        
        # Assert
        assert response.status_code == 400
        assert b'No file part' in response.data
    
    def test_empty_filename_returns_400(self, client):
        """Error cuando el archivo no tiene nombre"""
        # Arrange
        data = {
            'file': (io.BytesIO(b''), '')  # Nombre vacío
        }
        
        # Act
        response = client.post(
            '/api_proxy/generar_audio',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 400
        assert b'No selected file' in response.data
    
    @patch('api_proxy.routes.GoogleCloudTTSClient')
    def test_successful_audio_generation(self, mock_client_class, client, sample_xml):
        """Generación exitosa de audio"""
        # Arrange
        mock_client = Mock()
        mock_client.is_authenticated = True
        mock_response = Mock()
        mock_response.audio_content = b"audio_bytes"
        mock_client.synthesize_audio.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        data = {
            'file': (io.BytesIO(sample_xml.encode()), 'test.xml'),
            'language_code': 'es-ES',
            'voice_name': 'es-ES-Standard-A',
            'audio_format': 'MP3'
        }
        
        # Act
        response = client.post(
            '/api_proxy/generar_audio',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 200
        mock_client.synthesize_audio.assert_called_once_with(
            text=sample_xml,
            language_code='es-ES',
            voice_name='es-ES-Standard-A',
            audio_format='MP3'
        )
    
    @patch('api_proxy.routes.GoogleCloudTTSClient')
    def test_authentication_failure_returns_500(self, mock_client_class, client, sample_xml):
        """Error 500 cuando falla autenticación de Google Cloud"""
        # Arrange
        mock_client = Mock()
        mock_client.is_authenticated = False
        mock_client_class.return_value = mock_client
        
        data = {'file': (io.BytesIO(sample_xml.encode()), 'test.xml')}
        
        # Act
        response = client.post(
            '/api_proxy/generar_audio',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 500
        assert b'Error de autenticaci' in response.data
    
    @patch('api_proxy.routes.GoogleCloudTTSClient')
    def test_default_parameters(self, mock_client_class, client, sample_xml):
        """Verifica valores por defecto de parámetros"""
        # Arrange
        mock_client = Mock()
        mock_client.is_authenticated = True
        mock_client.synthesize.return_value = Mock(audio_content=b"audio")
        mock_client_class.return_value = mock_client
        
        data = {'file': (io.BytesIO(sample_xml.encode()), 'test.xml')}
        
        # Act
        client.post(
            '/api_proxy/generar_audio',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Assert - Verifica defaults
        call_kwargs = mock_client.synthesize_audio.call_args.kwargs
        assert call_kwargs['language_code'] == 'es-ES'
        assert call_kwargs['voice_name'] == 'es-ES-Standard-A'
        assert call_kwargs['audio_format'] == 'MP3'
    
    # @patch('api_proxy.routes.GoogleCloudTTSClient')
    # def test_is_long_parameter_parsing(self, mock_client_class, client, sample_xml):
    #     """Verifica que is_long se parsea correctamente desde string"""
    #     # Arrange
    #     mock_client = Mock()
    #     mock_client.is_authenticated = True
    #     mock_client.synthesize.return_value = Mock(audio_content=b"audio")
    #     mock_client_class.return_value = mock_client
        
    #     # Probar con 'true'
    #     data = {
    #         'file': (io.BytesIO(sample_xml.encode()), 'test.xml'),
    #         'is_long': 'true'
    #     }
        
    #     # Act
    #     client.post(
    #         '/api_proxy/generar_audio',
    #         data=data,
    #         content_type='multipart/form-data'
    #     )
        
        # Nota: En tu código actual 'is_long' no se usa, pero este test 
        # verificaría que al menos se recibe correctamente
        
        # Assert - Aquí verificarías que se llamó a algún método específico
        # para textos largos si implementaras esa lógica