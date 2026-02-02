from google.cloud import texttospeech
from typing import Union, BinaryIO
from ..exceptions import SynthesisError

class TextToSpeechSynthesizer:
    """Cliente para síntesis de texto a voz"""
    
    def __init__(self, authenticator: 'GoogleCloudAuthenticator'):
        self.authenticator = authenticator
        self._client = None
    
    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        """Lazy initialization del cliente TTS"""
        if self._client is None:
            credentials = self.authenticator.authenticate()
            self._client = texttospeech.TextToSpeechClient(credentials=credentials)
        return self._client
    
    def synthesize(
        self,
        text: str,
        language_code: str = "es-ES",
        ssml_gender: str = "es-US-Standard-A",
        audio_format: str = "MP3"
    ) -> texttospeech.SynthesizeSpeechResponse:
        """Sintetiza texto a audio"""
        try:
            # Configurar entrada de texto
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configurar la voz
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, ssml_gender)
            )
            
            # Configurar el audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=getattr(texttospeech.AudioEncoding, audio_format)
            )
            
            # Realizar la solicitud
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            return response
            
        except Exception as e:
            raise SynthesisError(f"Error en síntesis de audio: {str(e)}")
    
    def synthesize_to_file(
        self,
        text: str,
        output_file: Union[str, BinaryIO],
        **kwargs
    ) -> None:
        """Sintetiza texto y guarda en archivo"""
        response = self.synthesize(text, **kwargs)
        
        if isinstance(output_file, str):
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
        else:
            output_file.write(response.audio_content)