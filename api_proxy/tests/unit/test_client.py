import pytest
from unittest.mock import Mock, patch, MagicMock
from api_proxy.gcloud_tts.client import GoogleCloudTTSClient


class TestGoogleCloudTTSClientInitialization:
    """Tests de inicialización del cliente"""
    
    def test_client_initializes_components(self, mock_gcloud_client, mock_authenticator, mock_tts_synthesizer):
        """Verifica que el cliente inicializa todos sus componentes"""
        # Assert
        assert mock_gcloud_client.authenticator is mock_authenticator # Verifica el autenticador
        assert mock_gcloud_client.tts is mock_tts_synthesizer # Verifica el sintetizador
    
    # este test lo comento porque no tiene mucho sentido porque GoogleCloudCredentials no se llama en el init del cliente
    # def test_client_creates_credentials_without_json(self, mock_credentials):
    #     """Verifica que crea credenciales sin parámetro json"""
    #     # Arrange & Act
    #     with patch("gcloud_tts.client.GoogleCloudAuthenticator"), \
    #          patch("gcloud_tts.client.TextToSpeechSynthesizer"):
    #         client = GoogleCloudTTSClient()
        
    #     # Assert
    #     mock_credentials.assert_called_once_with() # Verifica que se crearon las credenciales


class TestGoogleCloudTTSClientAuthentication:
    """Tests de autenticación"""
    
    def test_is_authenticated_returns_true(self, mock_gcloud_client, mock_authenticator):
        """Verifica que is_authenticated delega al autenticador"""
        # Arrange
        mock_authenticator.is_authenticated = True
        
        # Act & Assert
        assert mock_gcloud_client.is_authenticated is True
    
    def test_is_authenticated_returns_false(self, mock_gcloud_client, mock_authenticator):
        """Verifica que detecta cuando no está autenticado"""
        # Arrange
        mock_authenticator.is_authenticated = False
        
        # Act & Assert
        assert mock_gcloud_client.is_authenticated is False


class TestSynthesizeAudio:
    """Tests del método synthesize_audio"""
    
    def test_synthesize_audio_returns_bytes(self, mock_gcloud_client, mock_tts_synthesizer):
        """Verifica que retorna el contenido de audio"""
        # Arrange
        text = "Hola mundo"
        mock_response = Mock()
        mock_response.audio_content = b"audio_content"
        mock_tts_synthesizer.synthesize.return_value = mock_response
        
        # Act
        result = mock_gcloud_client.synthesize_audio(text)
        
        # Assert
        assert result == b"audio_content"
        mock_tts_synthesizer.synthesize.assert_called_once_with(text)
    
    def test_synthesize_audio_passes_kwargs(self, mock_gcloud_client, mock_tts_synthesizer):
        """Verifica que pasa parámetros adicionales al sintetizador"""
        # Arrange
        text = "Hola"
        language_code = "es-ES"
        voice_name = "es-ES-Standard-B"
        
        # Act
        mock_gcloud_client.synthesize_audio(
            text, 
            language_code=language_code, 
            voice_name=voice_name
        )
        
        # Assert
        mock_tts_synthesizer.synthesize.assert_called_once_with(
            text, 
            language_code=language_code, 
            voice_name=voice_name
        )
    
    def test_synthesize_audio_saves_to_file_when_output_provided(self, mock_gcloud_client, mock_tts_synthesizer):
        """Verifica que guarda archivo cuando se proporciona output_file"""
        # Arrange
        text = "Hola mundo"
        output_file = "/tmp/output.mp3"
        
        # Act
        result = mock_gcloud_client.synthesize_audio(text, output_file=output_file)
        
        # Assert
        mock_tts_synthesizer.synthesize_to_file.assert_called_once_with(
            text, output_file
        )
        assert result == b"fake_audio_bytes_12345"  # Del fixture
    
    def test_synthesize_audio_does_not_save_file_when_no_output(self, mock_gcloud_client, mock_tts_synthesizer):
        """Verifica que no llama a synthesize_to_file sin output_file"""
        # Act
        mock_gcloud_client.synthesize_audio("Hola")
        
        # Assert
        mock_tts_synthesizer.synthesize_to_file.assert_not_called()