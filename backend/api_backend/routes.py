from flask import Blueprint, request, jsonify, current_app, send_file
import logging
import io
from .gcloud_tts.client import GoogleCloudTTSClient
from .utils.process_files import leer_docx_completo, extraer_texto_resaltado, convertir_a_formato_ssml, tamanio_archivo_en_megabytes
from .utils.validate import validar_procesar
import logging

# Configurar logging para que vaya a stdout (se captura con docker logs)
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# usamos blueprint porque es mas moderno que usar init_routes(app) y es mas fácil de testear
main_bp = Blueprint('main', __name__)        

@main_bp.route('/api/health', methods=['GET'])
def healthcheck():
    """Endpoint para verificar el estado de los servicios"""
    status = {
        "backend": "running",
        "cors": "enabled",
        "environment": "docker_compose"
    }
    
    # En Docker Compose, usar el nombre del servicio y puerto INTERNO
    possible_urls = [
        "http://api-proxy:5000/api_proxy/health",  # ✅ CORRECTO - nombre servicio + puerto interno
        "http://api-proxy-container:5000/api_proxy/health",  # ✅ nombre contenedor
    ]
    
    status["connection_attempts"] = {}
    
    for url in possible_urls:
        try:
            response = requests.get(url, timeout=5)
            status["api_proxy"] = "connected"
            status["api_proxy_url"] = url
            status["api_proxy_status"] = response.status_code
            status["api_proxy_response"] = response.json()
            status["connection_attempts"][url] = "success"
            break
        except Exception as e:
            status["connection_attempts"][url] = f"failed: {str(e)}"
    else:
        status["api_proxy"] = "disconnected"
    
    return jsonify(status), 200

@main_bp.route('/api/archivos_procesados')
def listar_archivos_procesados():
    import glob
    archivos = glob.glob("/app/shared-files/diario_procesado/*.docx")
    archivos_lista = [os.path.basename(archivo) for archivo in archivos]
    
    return jsonify({
        'directorio': os.path.abspath("/app/shared-files/diario_procesado/"),
        'archivos': archivos_lista,
        'total': len(archivos_lista)
    })

@main_bp.route('/audio/<filename>')
def serve_audio(filename):
    try:        
        # Verificar si el archivo existe
        if not os.path.exists(os.path.join(app.config['AUDIO_FOLDER'], filename)):
            return {"error": "Archivo no encontrado"}, 404
        
        return send_from_directory(
            app.config['AUDIO_FOLDER'], 
            filename,
            as_attachment=False,  # Para reproducir en el navegador
            mimetype='audio/mp3'
        )
    except Exception as e:
        return {"error": str(e)}, 500

@main_bp.route('/api/upload', methods=['POST'])
def upload_file():
    
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # logger.info(f"main.py - upload_file - 01 - Nombre del archivo subido: {FILENAME}")
    # Asegurarse de que el directorio existe (por si acaso)
    os.makedirs(app.config['SAVE_FOLDER'], exist_ok=True)

    file_path = os.path.join(app.config['SAVE_FOLDER'], file.filename)
    logger.info(f"main.py - upload_file - 01 - Guardando archivo en: {file_path}")
    file.save(file_path)
    logger.info(f"main.py - upload_file - 02 - El archivo se llama: {file.filename}")

    filename =file.filename.split('.')[0]

    doc_resaltado = "p_" + filename + ".docx"
    doc_resaltado_path = os.path.join('/app/shared-files/diario_procesado/', doc_resaltado)
    extraer_texto_resaltado(file_path, doc_resaltado_path)
    logger.info("main.py - upload_file - 03 - Documento procesado con texto resaltado guardado en: " + doc_resaltado_path)     

    doc_ssml = "ssml_" + filename + ".xml"
    doc_ssml_path = os.path.join('/app/shared-files/diario_ssml/', doc_ssml)
    palabras_caracteres = convertir_a_formato_ssml(doc_resaltado_path, doc_ssml_path)
    logger.info("main.py - upload_file - 03 - Documento xml" + doc_ssml)     
    logger.info("main.py - upload_file - 03 - Documento procesado con texto resaltado guardado en: " + doc_ssml_path)     
    
    tamanio_megabytes_archivo = tamanio_archivo_en_megabytes(doc_ssml_path)

    logger.info("main.py - upload_file - 04 - Documento convertido a formato ssml y guardado en: " + doc_ssml_path)     

    response_data = {"status": "OK", "Cantidad de palabras en SSML:": palabras_caracteres[0], "Cantidad de caracteres en SSML": palabras_caracteres[1], "Tamaño del archivo SSML en megabytes" : tamanio_megabytes_archivo }
    logger.info (f"main.py - upload_file - 05 - {response_data}")
    
    return jsonify({"palabras:": palabras_caracteres[0], "caracteres": palabras_caracteres[1], "tamanio" : tamanio_megabytes_archivo }), 200

@main_bp.route('/api/generar_audio', methods=['GET'])
# @secure_endpoint # Este endpoint solo puede ser llamado desde el frontend
def generar_audio():
    # no recibo un archivo porque el archivo ya fue subido previamente y procesado
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename parameter is required'}), 400

    ssml_filename = "ssml_" + filename.split('.')[0] + ".xml"
    file_path = os.path.join('/app/shared-files/diario_ssml', ssml_filename)

    logging.info(f"main.py - generar_audio - 01 - Nombre del archivo SSML: {ssml_filename}")

    logging.info(f"main.py - generar_audio - 01 - Nombre del archivo SSML: {file_path}")
    # Leer archivo como BYTES para multipart
    with open(file_path, 'rb') as f:
        content_bytes = f.read()
    # Sirve para ver tamaño del archivo 
    content = leer_archivo_ssml(file_path)
    is_long = len(content) > 5000
    files = {
        'file': (ssml_filename, content_bytes, 'application/xml')
    }

    data = {
        'language_code': 'es-ES',
        'voice_name': 'es-ES-Standard-A',
        'audio_format': 'WAV' if is_long else 'MP3' # si es largo uso WAV
    }

    response = requests.post('http://api-proxy:5000/api_proxy/generar_audio', files=files, data=data, timeout=30)

    if response.status_code == 200:
        try:
            result = response.json()     
            logger.info(f"main.py - generar_audio - 01 - Generando audio para el archivo: {result[0]}")
            destino_local = AUDIO_FOLDER
            os.makedirs(destino_local, exist_ok=True)

            # Crear nombre de archivo para el audio
            filename_sin_extension = filename.split('.')
            # si existe el archivo con extensión wav lo voy a transformar a ogg
            audio_file = f"{filename_sin_extension[0]}.wav"
            audio_path = os.path.join(destino_local, audio_file)
            output_mp3_path = os.path.join(destino_local, f"{filename_sin_extension[0]}.mp3")
            
            if os.path.isfile(audio_path):
                try:
                    logger.info(f"main.py - generar_audio - 02 - Path del audio: {audio_path}")
                    # Cargar audio
                    audio = AudioSegment.from_wav(audio_path)
                    # Convertir a MP3                    
                    audio.export(
                        output_mp3_path,
                        format='mp3',
                        bitrate='160k',
                        tags={
                            'title': os.path.basename(output_mp3_path),
                            'artist': 'Audio App',
                            'album': 'Diarios'
                        }
                    )
                    
                    # Eliminar WAV original si se solicita
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        print(f"🗑️  Eliminado WAV original")
        
                except Exception as error_convert:
                    logger.info(f"❌ Error en la conversión WAV a MP3: {error_convert}")

            return jsonify({"status": "OK", "message": "Archivo de audio generado"}), 200

        except Exception as e:
            logger.info(f"main.py - generar_audio - 03 - Error procesando audio: {e}")
            return jsonify({"status": "ERROR", "message": f"Error procesando audio: {e}"}), 500
    else:
        logger.info(f"main.py - generar_audio - 04 - Error llamando a api-proxy: {response.status_code}")
        return jsonify({"status": "ERROR", "message": "Error llamando a api-proxy"}), 500
