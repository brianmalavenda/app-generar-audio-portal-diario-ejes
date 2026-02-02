from flask import request, jsonify, send_file
import logging
import io
from .gcloud_tts.client import GoogleCloudTTSClient
from .utils.process_files import leer_docx_completo
from .utils.validate import validar_procesar

logger = logging.getLogger(__name__)

def init_routes(app):
    """Registra todas las rutas en la app"""
        
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
            
            logger.info(f"api_proxy - generar_audio - Archivo recibido: {file.filename}")
            logger.info(f"api_proxy - generar_audio - Tamaño contenido: {len(xml_content)} chars")
            
            # 4. Obtener metadata del form data (NO de request.get_json())
            # is_long = request.form.get('is_long', 'false').lower() == 'true'
            language_code = request.form.get('language_code', 'es-ES')
            voice_name = request.form.get('voice_name', 'es-ES-Standard-A')
            audio_format = request.form.get('audio_format', 'MP3') # Valores posibles: MP3, WAV, OGG_OPUS, LINEAR16
            
            logger.info(f"api_proxy - generar_audio - Parámetros: language={language_code}, format={audio_format}")
            
            # 5. Inicializar cliente Google Cloud
            gcloud_client = GoogleCloudTTSClient()
            
            if not gcloud_client.is_authenticated:
                logger.error("api_proxy - generar_audio - Error de autenticación Google Cloud")
                return jsonify({'error': 'Error de autenticación con Google Cloud'}), 500
            
            result = gcloud_client.synthesize_audio(
                text=xml_content,
                language_code=language_code,
                voice_name=voice_name, 
                audio_format=audio_format # si is_long es True, usar WAV
            )
            
            # 7. Preparar response (asegúrate de tener acceso a audio_content)
            audio_content = result.audio_content if hasattr(result, 'audio_content') else result
            
            logger.info(f"api_proxy - generar_audio - Audio generado: {len(audio_content)} bytes")
            
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
            logger.error(f"api_proxy - generar_audio - Error: {str(e)}", exc_info=True)
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500

    @app.get("/api_proxy/health")
    def health():
        return {"message": "Mandame un audio que te lo traduzco al toque"}