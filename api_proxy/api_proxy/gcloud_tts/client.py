from typing import Optional
from .auth.credentials import GoogleCloudCredentials
from .auth.authenticator import GoogleCloudAuthenticator
from .tts.synthesizer import TextToSpeechSynthesizer

class GoogleCloudTTSClient:
    """Cliente principal para Text-to-Speech de Google Cloud"""
    
    def __init__(
        self
        # credentials_json: Optional[str] = None
    ):
        # Crear credenciales
        # credentials_json=credentials_json, lo cargo directamente de un secreto
        # credentials = GoogleCloudCredentials()
        
        # Inicializar componentes
        self.authenticator = GoogleCloudAuthenticator()
        credenciales = self.authenticator.authenticate()
        if not self.authenticator.is_authenticated:
                logger.error("api_proxy - inicializar - Error de autenticación Google Cloud")
                raise ValueError("Error de autenticación con Google Cloud")
            
        self.tts = TextToSpeechSynthesizer(credenciales=credenciales)
    
    def synthesize_audio(
        self,
        output_file_name: str,
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
        return self.tts.synthesize(output_file_name=output_file_name, text=text, **kwargs)
        
        #if output_file:
            # output_file es opcional, si se proporciona se guarda el audio en ese archivo
            # self.tts.synthesize_to_file(output_file_name=output_file_name, text=text, **kwargs)
        
        # return response.audio_content
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si el cliente está autenticado"""
        return self.authenticator.is_authenticated