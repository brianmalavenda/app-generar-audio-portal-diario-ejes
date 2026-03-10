from flask import Blueprint, jsonify, current_app, send_file, request, session
from werkzeug.utils import secure_filename
import uuid
import requests
import logging
import io
import os
import sys
from .utils.process_file import extraer_texto_resaltado, convertir_a_formato_ssml, tamanio_archivo_en_megabytes, contar_cantidad_de_palabras, contar_cantidad_de_caracteres
from repositories.file_repository import FileRepository

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
#solo en fastApi @description("Endpoint para verificar el estado de los servicios") 
def healthcheck():
    """Endpoint para verificar el estado de los servicios"""
    status = {
        "backend": "running",
        "cors": "enabled",
        "environment": "docker_compose"
    }
    
    # En Docker Compose, usar el nombre del servicio y puerto INTERNO
    possible_urls = [
        "http://api_proxy:5000/api_proxy/health",  # ✅ CORRECTO - nombre servicio + puerto interno
        "http://api_proxy-container:5000/api_proxy/health",  # ✅ nombre contenedor
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
#solo en fastApi @description("Endpoint para listar los archivos procesados en el directorio compartido. Archivo procesado es el que tiene el texto resaltado extraído y guardado en formato docx.")
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
#solo en fastApi @description("Endpoint para servir archivos de audio. Utilizado para reproducir el audio generado en el frontend. El archivo debe existir en el directorio de audio configurado.")
def serve_audio(filename):
    try:        
        # Verificar si el archivo existe
        if not os.path.exists(os.path.join(current_app.config['AUDIO_FOLDER'], filename)):
            return {"error": "Archivo no encontrado"}, 404
        
        return send_from_directory(
            current_app.config['AUDIO_FOLDER'], 
            filename,
            as_attachment=False,  # Para reproducir en el navegador
            mimetype='audio/mp3'
        )
    except Exception as e:
        return {"error": str(e)}, 500

@main_bp.route('/api/upload', methods=['POST'])
#solo en fastApi @description("Endpoint para subir un archivo, procesarlo y generar un SSML. El archivo se guarda en el directorio compartido, se extrae el texto resaltado, se convierte a formato SSML y se devuelve información sobre el proceso.")
def upload_file():
    
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400    

    # valido a través de la biblioteca secure_filename que el nombre del archivo no tenga caracteres extraños para usuarios que intente alguna inyección de datos o
    # sobreescribir archivos de sistema modificando la ruta donde se almacena
    if file and file.filename != '':
        nombre_seguro = secure_filename(file.filename)
        if nombre_seguro != '':
            file.filename = nombre_seguro

    # logger.info(f"main.py - upload_file - 01 - Nombre del archivo subido: {FILENAME}")
    # Asegurarse de que el directorio existe (por si acaso)
    os.makedirs(current_app.config['SAVE_FOLDER'], exist_ok=True)

    file_path = os.path.join(current_app.config['SAVE_FOLDER'], file.filename)
    logger.info(f"main.py - upload_file - 01 - Guardando archivo en: {file_path}")
    file.save(file_path)
    logger.info(f"main.py - upload_file - 02 - El archivo se llama: {file.filename}")

    filename =file.filename.split('.')[0]

    doc_resaltado = "p_" + filename + ".docx"
    doc_resaltado_path = os.path.join('/app/shared-files/diario_procesado/', doc_resaltado)
    extraer_texto_resaltado(file_path, doc_resaltado_path)
    logger.info("main.py - upload_file - 03 - Documento procesado con texto resaltado guardado en: " + doc_resaltado_path)     

    cantidad_palabras = contar_cantidad_de_palabras(doc_resaltado_path)
    cantidad_catacteres = contar_cantidad_de_caracteres(doc_resaltado_path)
    # Esto lo dejamos para la 1er iteración

    # doc_ssml = "ssml_" + filename + ".xml"
    # doc_ssml_path = os.path.join('/app/shared-files/diario_ssml/', doc_ssml)
    # palabras_caracteres = convertir_a_formato_ssml(doc_resaltado_path, doc_ssml_path)
    # logger.info("main.py - upload_file - 03 - Documento xml" + doc_ssml)     
    # logger.info("main.py - upload_file - 03 - Documento procesado con texto resaltado guardado en: " + doc_ssml_path)     
    tamanio_megabytes_archivo = tamanio_archivo_en_megabytes(doc_resaltado_path)
    # logger.info("main.py - upload_file - 04 - Documento convertido a formato ssml y guardado en: " + doc_ssml_path)     

    try:
        # Una sola línea para guardar en BD
        file_id = FileRepository.create(
            original_filename=file.filename,
            original_path=file_path,
            processed_filename=doc_resaltado,
            processed_path=doc_resaltado_path,
            ssml_word_count=cantidad_palabras,
            ssml_char_count=cantidad_catacteres,
            ssml_file_size_mb=tamanio_megabytes_archivo,
            status='processed',
            session_id=session.get('session_id', '')
        )

        return jsonify({
        'status': 'OK', 
        'file_id': inserted_id, # El frontend usará este ID para el siguiente paso
        'metadata': {"filename": doc_resaltado, "palabras:": cantidad_palabras, "caracteres": cantidad_catacteres, "tamanio" : tamanio_megabytes_archivo } # Puedes devolver metadatos si quieres
        }), 200

    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

@main_bp.route('/api/generar_audio', methods=['GET'])
#solo en fastApi @description("Endpoint para generar un archivo de audio a partir de un archivo SSML previamente procesado. El nombre del archivo SSML se recibe como parámetro, se lee el contenido, se envía a la API proxy para generar el audio, y luego se convierte a MP3 si es necesario. El audio generado se guarda en el directorio configurado y se devuelve información sobre el proceso.")
# @secure_endpoint # Este endpoint solo puede ser llamado desde el frontend
def generar_audio():
    data = request.get_json()
    file_id = data.get('file_id') # El frontend te envía el ID que le diste

    if not file_id:
            return jsonify({'error': 'File id parameter is required'}), 400

    file_record = FileRepository.find_by_id(file_id)
    if not file_record:
        return jsonify({'error': 'File ID not found'}), 404

    logging.info(f"main.py - generar_audio - 00 - File ID: {file_id}")

    ruta_archivo_procesado = file_record['processed_path']
    filename = file_record['original_filename']
    cant_palabras = file_record['processed_word_count']
    file_path = os.path.join('/app/shared-files/diario_procesado', filename)

    # por ahora vamos ausar una sola voz y lenguaje
    # 1ra iteracón: "splitear" el ssml_filename por cada título de noticia y por cada cuerpo de noticia. El título tendra una configuración especial de voz y el cuerpo otra.
    # 2da iteración: usaremos esto para generar audios en el EDM por lo tanto incluiremos una configuración especial para volanta y copete. Ligeramente distanta.
    # esto dará la impresión de que es un noticiero leyendo el diario o un "postcast" diario.
    logging.info(f"main.py - generar_audio - 01 - Nombre del archivo SSML: {file_path}")
    
    # Leer archivo como BYTES para multipart
    with open(file_path, 'rb') as f:
        content_bytes = f.read()
    # Sirve para ver tamaño del archivo 

    is_long = cant_palabras > 5000
    files = {
        'file': (filename, content_bytes, 'application/xml')
    }

    data = {
        'language_code': 'es-ES',
        'voice_name': 'es-ES-Standard-A',
        'audio_format': 'WAV' if is_long else 'MP3' # si es largo uso WAV
    }

    response = requests.post('http://api_proxy:5000/api_proxy/generar_audio', files=files, data=data, timeout=30)

    if response.status_code == 200:
        try:
            result = response.json()     
            logger.info(f"main.py - generar_audio - 01 - Generando audio para el archivo: {result[0]}")
            
            # Crear nombre de archivo para el audio
            filename_sin_extension = filename.split('.')
            # si existe el archivo con extensión wav lo voy a transformar a ogg
            audio_file = f"{filename_sin_extension[0]}.wav"
            audio_path = os.path.join(current_app.config['AUDIO_FOLDER'], audio_file)
            output_mp3_path = os.path.join(current_app.config['AUDIO_FOLDER'], f"{filename_sin_extension[0]}.mp3")
            
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
                        
                    actualizado = FileRepository.update_audio_path(file_id, audio_path)
                    if not actualizado:
                        return jsonify({'warning': 'Audio generado pero no se pudo actualizar el registro'}), 202
                        
                except Exception as error_convert:
                    logger.info(f"❌ Error en la conversión WAV a MP3: {error_convert}")

            return jsonify({"status": "OK", "message": "Archivo de audio generado"}), 200

        except Exception as e:
            logger.info(f"main.py - generar_audio - 03 - Error procesando audio: {e}")
            return jsonify({"status": "ERROR", "message": f"Error procesando audio: {e}"}), 500

    else:
        logger.info(f"main.py - generar_audio - 04 - Error llamando a api-proxy: {response.status_code}")
        return jsonify({"status": "ERROR", "message": "Error llamando a api-proxy"}), 500
