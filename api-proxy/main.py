from gcloud_tts import GoogleCloudTTSClient
from dotenv import load_dotenv
import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  
from gcloud_SA_access import get_access_token_service_account, get_project_id_service_account, sintetizar_audio
from utils import leer_docx_completo, validar_procesar
from dataclasses import dataclass
import json
import logging
import sys

# Configurar logging para que vaya a stdout (se captura con docker logs)
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
ALLOWED_ORIGINS = ['http://localhost:3000','http://localhost']
CORS(app, origins=ALLOWED_ORIGINS)
# carga las variables del archivo .env
load_dotenv()

@dataclass
class FileInfo:
    name: str = "test"
    content: str = None
    is_long: bool = False   

## Este endpoint recibe un nombre de archivo por parametro ?filename=ssml_test_03.xml
# @app.post("/api_proxy/generar_audio_from_file/upload")
# async def generar_audio_from_file(
#     file: UploadFile = File(..., description="Archivo XML/SSML o texto"),
#     language_code: str = Form("es-ES"),
#     voice_name: str = Form("es-ES-Standard-A"),
#     audio_format: str = Form("MP3")
# ):
@app.route('/api_proxy/generar_audio', methods=['POST'])
def generar_audio():
    data = request.get_json()
    # return jsonify({"recibido": data}), 200

    # Validar extensión
    # allowed_extensions = {'.xml', '.ssml', '.txt'}
    # file_ext = os.path.splitext(file.filename)[1].lower()

     if data.content is None:
        raise HTTPException(
            400, 
            f"No se envío el contendi a procesar"
        )
    
    logger.info(f"api-proxy - api - generar_audio - 01 - Contenido del archivo leído correctamente")
    
    gcloud_client = GoogleCloudTTSClient()
    
    if not gcloud_client.is_authenticated():
        return jsonify({'error': 'Error de autenticación con Google Cloud'}, 500)

    try:
        #result = sintetizar_audio(gcloud_session, file)
        if data.is_long:
            result = gcloud_client.synthesize(
                text = data.content,
                # output_file = f"/app/shared-files/audios/{file.name}.mp3",
                audio_format = "WAV",
                language_code = "es-ES"
            ).audio_content
        else:
            result = gcloud_client.synthesize(
                text = data.content,
                # output_file = f"/app/shared-files/audios/{file.name}.mp3",
                audio_format = "WAV",
                language_code = "es-ES"
            ).audio_content
        
        # Crear stream en memoria
        audio_stream = io.BytesIO(result)
        
        # Devolver como streaming response
        return StreamingResponse(
            audio_stream,
            media_type=content_types.get(audio_format, "audio/mpeg"),
            headers={
                "Content-Disposition": f'inline; filename="tts_audio.{audio_format.lower()}"',
                "X-TTS-Text-Length": str(len(data.content)),
                "X-TTS-Language": language_code
            }
        )

        logger.info(f"api-proxy - api - generar_audio - 03 - Resultado de la síntesis: {result}")  # Imprime solo los primeros 100 caracteres del resultado
        if result:
            return jsonify({'status': 'success', 'message': 'Audio generated successfully'},200)
        else:
            return jsonify({'status': 'error', 'message': 'Audio synthesis failed'}, 500)    

        logger.info(f"-------api-proxy - main.py - generar_audio - 04 - Estado de la síntesis: {ok}")
    except Exception as e:
        logger.info(f"api-proxy - main.py - generar_audio - 04 - Error en generar_audio: {str(e)}")
        return jsonify({'error': 'Internal server error'}, 500)
    
@app.get("/api_proxy/health")
def health():
    return {"message": "Mandame un audio que te lo traduzco al toque"}

if __name__ == '__main__':
    #Dentro de un contenedor, localhost es solo el contenedor mismo. Si quieres que otro contenedor lo vea, Flask debe escuchar en 0.0.0.0 (todas las interfaces de red).
    app.run(host='0.0.0.0', port=5000, debug=True)