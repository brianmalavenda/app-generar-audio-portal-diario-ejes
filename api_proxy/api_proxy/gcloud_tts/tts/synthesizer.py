from google.cloud import texttospeech, storage
from google.oauth2 import service_account
import io
from flask import send_file, Response, jsonify
import logging
from typing import Union, BinaryIO
from ..exceptions import SynthesisError

class TextToSpeechSynthesizer:
    """Cliente para síntesis de texto a voz"""
    
    def __init__(self, credenciales: service_account.Credentials):
        self._credentials = credenciales
        self._client = texttospeech.TextToSpeechClient(credentials=credenciales)
    
    # @property
    # def client(self) -> texttospeech.TextToSpeechClient:
    #     """Lazy initialization del cliente TTS"""
    #     if self._client is None:
    #         credentials = self.authenticator.authenticate()
    #         self._client = texttospeech.TextToSpeechClient(credentials=credentials)
    #     return self._client
    def synthesize(
        self,
        output_file_name: str,
        text: str,
        language_code: str = "es-ES",
        voice_name: str = "es-ES-Standard-A",
        audio_format: str = "MP3"
    ) -> texttospeech.SynthesizeSpeechResponse:
        """Sintetiza texto a audio"""
        try:
            # Configurar entrada de texto
            if text.strip().startswith("<speak>"):
                synthesis_input = texttospeech.SynthesisInput(ssml=text)
            else:
                synthesis_input = texttospeech.SynthesisInput(text=text)
            # Configurar la voz
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )
            
            print(f"Configuración de síntesis: language_code={language_code}, voice_name={voice_name}, audio_format={audio_format}")
            # mostramos la voz seleccionada para depuración
            print(f"Voz seleccionada: {voice}")

            # Configurar el audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=getattr(texttospeech.AudioEncoding, audio_format)
            )
            
            # Realizar la solicitud
            # response = self._client.synthesize_speech(
            #     input=synthesis_input,
            #     voice=voice,
            #     audio_config=audio_config
            # )

            project_id = self._credentials.project_id
            parent = f"projects/{project_id}/locations/us-central1"
            output_gcs_uri= f"gs://audios-text-to-speech-01/{output_file_name}"

            request = texttospeech.SynthesizeLongAudioRequest(
                parent=parent,
                input=synthesis_input,
                audio_config=audio_config,
                voice=voice,
                output_gcs_uri=output_gcs_uri,
            )


            # self._client no tiene el método synthesize_long_audio, por eso creo un nuevo cliente específico para esta función
            client = texttospeech.TextToSpeechLongAudioSynthesizeClient(credentials=self._credentials)
            operation = client.synthesize_long_audio(request=request)
            result = operation.result(timeout=300)
            # 1. Creamos cliente de Storage con las mismas credenciales
            storage_client = storage.Client(credentials=self._credentials)
            
            # 2. Apuntamos al bucket y al archivo
            bucket_name = "audios-text-to-speech-01"
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(output_file_name)

            # 3. Descargamos los bytes
            audio_content = blob.download_as_bytes()
            
            print(f"Audio descargado con éxito: {len(audio_content)} bytes")
            
            # Devolvemos los bytes para que tu API pueda enviarlos
            return audio_content
            
        except Exception as e:
            raise SynthesisError(f"Error en síntesis de audio: {str(e)}")
    
    # def synthesize_to_file(
    #     self,
    #     text: str,
    #     output_file: Union[str, BinaryIO],
    #     **kwargs
    # ) -> None:
    #     """Sintetiza texto y guarda en archivo"""
    #     response = self.synthesize(text, **kwargs)
        
    #     if isinstance(output_file, str):
    #         with open(output_file, "wb") as out:
    #             out.write(response.audio_content)
    #     else:
    #         output_file.write(response.audio_content)