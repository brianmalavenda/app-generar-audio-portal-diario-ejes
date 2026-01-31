from typing import Optional
from .auth.credentials import GoogleCloudCredentials
from .auth.authenticator import GoogleCloudAuthenticator
from .tts.synthesizer import TextToSpeechSynthesizer

class GoogleCloudTTSClient:
    """Cliente principal para Text-to-Speech de Google Cloud"""
    
    def __init__(
        self,
        credentials_json: Optional[str] = None
    ):
        # Crear credenciales
        # credentials_json=credentials_json, lo cargo directamente de un secreto
        credentials = GoogleCloudCredentials()
        
        # Inicializar componentes
        self.authenticator = GoogleCloudAuthenticator(credentials)
        self.tts = TextToSpeechSynthesizer(self.authenticator)
    
    def synthesize_audio(
        self,
        text: str,
        output_file: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Método principal para sintetizar audio.
        
        Args:
            text: Texto a sintetizar
            output_file: Ruta del archivo de salida (opcional)
            **kwargs: Parámetros adicionales para synthesize()
        
        Returns:
            bytes: Contenido de audio
        """
        response = self.tts.synthesize(text, **kwargs)
        
        if output_file:
            self.tts.synthesize_to_file(text, output_file, **kwargs)
        
        return response.audio_content
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si el cliente está autenticado"""
        return self.authenticator.is_authenticated