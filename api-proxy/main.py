from gcloud_tts import GoogleCloudTTSClient
from dotenv import load_dotenv
import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  
from .utils import leer_docx_completo, validar_procesar
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
    try:
        # 1. Verificar archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        
        # 2. Verificar que se subió un archivo
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 3. Leer contenido XML
        xml_content_bytes = file.read()
        xml_content = xml_content_bytes.decode('utf-8')
        
        logger.info(f"api-proxy - generar_audio - Archivo recibido: {file.filename}")
        logger.info(f"api-proxy - generar_audio - Tamaño contenido: {len(xml_content)} chars")
        
        # 4. Obtener metadata del form data (NO de request.get_json())
        is_long = request.form.get('is_long', 'false').lower() == 'true'
        language_code = request.form.get('language_code', 'es-ES')
        voice_name = request.form.get('voice_name', 'es-ES-Standard-A')
        audio_format = request.form.get('audio_format', 'MP3')
        
        logger.info(f"api-proxy - generar_audio - Parámetros: is_long={is_long}, language={language_code}, format={audio_format}")
        
        # 5. Inicializar cliente Google Cloud
        gcloud_client = GoogleCloudTTSClient()
        
        if not gcloud_client.is_authenticated:
            logger.error("api-proxy - generar_audio - Error de autenticación Google Cloud")
            return jsonify({'error': 'Error de autenticación con Google Cloud'}), 500
        
        # 6. Sintetizar audio (mismo código para ambos casos según veo)
        result = gcloud_client.synthesize(
            text=xml_content,
            language_code=language_code,
            voice_name=voice_name,
            audio_format=audio_format
        )
        
        # 7. Preparar response (asegúrate de tener acceso a audio_content)
        audio_content = result.audio_content if hasattr(result, 'audio_content') else result
        
        logger.info(f"api-proxy - generar_audio - Audio generado: {len(audio_content)} bytes")
        
        # 8. Devolver como streaming response
        content_types = {
            "MP3": "audio/mpeg",
            "WAV": "audio/wav",
            "OGG_OPUS": "audio/ogg",
            "LINEAR16": "audio/wav"
        }
        
        # Crear stream en memoria
        audio_stream = io.BytesIO(audio_content)
        
        # Devolver como streaming response
        return send_file(
            audio_stream,
            mimetype=content_types.get(audio_format, "audio/mpeg"),
            as_attachment=True,
            download_name=f"audio_{file.filename}.{audio_format.lower()}"
        )
        # O usando Response de Flask:
        # return Response(
        #     audio_content,
        #     mimetype=content_types.get(audio_format, "audio/mpeg"),
        #     headers={
        #         "Content-Disposition": f'attachment; filename="audio_{file.filename}.{audio_format.lower()}"'
        #     }
        # )
        
    except Exception as e:
        logger.error(f"api-proxy - generar_audio - Error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
@app.get("/api_proxy/health")
def health():
    return {"message": "Mandame un audio que te lo traduzco al toque"}

if __name__ == '__main__':
    #Dentro de un contenedor, localhost es solo el contenedor mismo. Si quieres que otro contenedor lo vea, Flask debe escuchar en 0.0.0.0 (todas las interfaces de red).
    app.run(host='0.0.0.0', port=5000, debug=True)