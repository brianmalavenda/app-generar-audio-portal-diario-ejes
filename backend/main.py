# -*- coding: utf-8 -*-
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import os
import xml.dom.minidom
from flask import Flask, request, jsonify, send_file, send_from_directory
import requests
from flask_cors import CORS, cross_origin  # Importa la extensión CORS
from utils.convert_audio import optimize_audio
import os
from functools import wraps
from dotenv import load_dotenv
import datetime
import logging
from dataclasses import dataclass
import sys

@dataclass
class OptimizeAudio:
    original: str = "0 MB"
    comprimido: str = "0 MB"
    ratio_compresion: str = "0 %"

# Configurar logging para que vaya a stdout (se captura con docker logs)
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# load_dotenv()
# ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app = Flask(__name__)
# Usar ruta absoluta con valor por defecto
AUDIO_FOLDER = os.getenv('AUDIO_FOLDER', '/app/shared-files/audio/')
# os.path.join(os.getcwd(), "/app/shared-files", "audio")
SAVE_FOLDER = os.getenv('SAVE_FOLDER', '/app/shared-files/diario_pintado/')
PROCESADOS = os.getenv('PROCESADOS', '/app/shared-files/diario_procesado/')
# Configura CORS para permitir solicitudes desde localhost:3000

ALLOWED_ORIGINS = ['http://localhost:3000']  # Agrega tu dominio de producción
CORS(app, origins=ALLOWED_ORIGINS)
# CORS(app, resources={
#     r"/api/*": {
#         "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
#         "methods": ["GET", "POST"],
#         "allow_headers": ["Content-Type"]
#     }
# })

class Heading1NotFoundException(Exception):
    """Excepción personalizada para cuando no se encuentra un Heading 1"""
    pass

@app.route('/api/healthcheck', methods=['GET'])
@cross_origin(origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
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

# Middleware de seguridad combinado
def secure_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar Origin
        origin = request.headers.get('Origin')
        if origin and origin not in ALLOWED_ORIGINS:
            return jsonify({'error': 'Cross-origin request not allowed'}), 403
        
        # Verificar Referer (backup)
        referer = request.headers.get('Referer')
        if referer and not any(allowed in referer for allowed in ALLOWED_ORIGINS):
            return jsonify({'error': 'Access denied'}), 403
        
        # Verificar que no sea acceso directo (opcional)
        user_agent = request.headers.get('User-Agent', '')
        if 'Mozilla' not in user_agent:  # No es un navegador
            return jsonify({'error': 'Browser access required'}), 403
        elif 'Brave' not in user_agent:  
            return jsonify({'error': 'Browser access required'}), 403
        elif 'Chrome' not in user_agent:  
            return jsonify({'error': 'Browser access required'}), 403
        elif 'Firefox' not in user_agent:  
            return jsonify({'error': 'Browser access required'}), 403
        elif 'Safari' not in user_agent:  
            return jsonify({'error': 'Browser access required'}), 403

        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/archivos_procesados')
def listar_archivos_procesados():
    import glob
    archivos = glob.glob("/app/shared-files/diario_procesado/*.docx")
    archivos_lista = [os.path.basename(archivo) for archivo in archivos]
    
    return jsonify({
        'directorio': os.path.abspath("/app/shared-files/diario_procesado/"),
        'archivos': archivos_lista,
        'total': len(archivos_lista)
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    
    FILENAME = file.filename
    logger.info(f"main.py - upload_file - 01 - Nombre del archivo subido: {FILENAME}")
    # Asegurarse de que el directorio existe (por si acaso)
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    file_path = os.path.join(SAVE_FOLDER, file.filename)
    logger.info(f"main.py - upload_file - 02 - Guardando archivo en: {file_path}")
    file.save(file_path)
    logger.info(f"main.py - upload_file - 03 - El archivo se llama: {file.filename}")

    filename_sin_extension = file.filename.split('.')
    
    nombre_archivo_procesado = "procesado_" + filename_sin_extension[0] + ".docx"
    logger.info(f"main.py - upload_file - 04 - Nombre de mi archivo procesado {nombre_archivo_procesado}")
    documento_salida = os.path.join('/app/shared-files/diario_procesado/', nombre_archivo_procesado)
 
    nombre_archivo_ssml = "ssml_" + filename_sin_extension[0] + ".xml"
    logger.info(f"main.py - upload_file - 05 - Nombre de mi archivo ssml {nombre_archivo_ssml}")
    xml_salida = os.path.join('/app/shared-files/diario_ssml/', nombre_archivo_ssml)
    
    extraer_texto_resaltado(file_path, documento_salida)
    logger.info("main.py - upload_file - 06 - Procese el documento y extraje lo resaltado, vamos bien")
    
    palabras_caracteres = convertir_a_formato_ssml(documento_salida, xml_salida)
    tamanio_megabytes_archivo = tamanio_archivo_en_megabytes(xml_salida)
    response_data = {"status": "OK", "Cantidad de palabras en SSML:": palabras_caracteres[0], "Cantidad de caracteres en SSML": palabras_caracteres[1], "Tamaño del archivo SSML en megabytes" : tamanio_megabytes_archivo }
    logger.info (f"main.py - upload_file - 06 - {response_data}")
    
    return jsonify({"palabras:": palabras_caracteres[0], "caracteres": palabras_caracteres[1], "tamanio" : tamanio_megabytes_archivo }), 200

@app.route('/api/descargar_doc_procesado', methods=['POST'])
def descargar_doc_procesado():
    filename = request.json.get('filename')  # Ahora viene en el body
    
    if not filename:
        return jsonify({'error': 'Filename parameter is required'}), 400
    
    # Sanitizar el filename para seguridad
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Invalid filename'}), 400
    
    file_path = os.path.join("procesados/", filename)
    
    logger.info (f"main.py - descargar_doc_procesado - 01 - Buscando archivo en: {file_path}")  # Debug
    logger.info (f"main.py - descargar_doc_procesado - 02 - Archivo existe: {os.path.exists(file_path)}")  # Debug

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Verificar que es un archivo y no un directorio
        if not os.path.isfile(file_path):
            return jsonify({'error': 'Path is not a file'}), 400
            
        # Debug: información del archivo
        file_stats = os.stat(file_path)
        logger.info (f"main.py - descargar_doc_procesado - 03 - Tamaño del archivo: {file_stats.st_size} bytes")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            conditional=True  # Esto permite el 304 para cache, pero fuerza descarga si es necesario
        )
    except Exception as e:
        logger.info (f"main.py - descargar_doc_procesado - 04 - Error al enviar archivo: {e}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

def extraer_texto_resaltado(input_path, output_path):
    """
    Extrae texto resaltado en amarillo de un documento Word y lo guarda en un nuevo documento.
    Args:
        input_path (str): Ruta al documento Word de entrada (.docx)
        output_dir (str): Directorio donde se guardará el nuevo documento con el texto extraído
    """
    try:
        # Cargar el documento
        doc = Document(input_path)        
        nuevo_doc = Document()
        contador_notas = 0
        nota = []
        
        for paragraph in doc.paragraphs:
            # Iterar a través de todos los "runs" (fragmentos de texto con formato) en el párrafo
            # busca titulos de notas  
            if paragraph.style.name.startswith('Heading 1'):
                if len(nota) == 0:
                    #creo la primera nota
                    nota.append({
                        "id": contador_notas,
                        "titulo": paragraph.text,
                        "cuerpo": [],
                        "estado": "pendiente" # la nota cambiara de estado a completa cuando se acabe el documento o cuando se encuentre otro heading 1
                    })
                else:
                    # Si encontramos otro Heading 1, validamos que la nota tenga cuerpo antes de iniciar una nueva
                    if len(nota[contador_notas]["cuerpo"]) > 0:
                        nota[contador_notas]["estado"] = "completa"
                        # print(f"Nota completa: {nota}")
                        contador_notas += 1
                        # Iniciar una nueva nota
                        nota.append({
                            "id": contador_notas,
                            "titulo": paragraph.text,
                            "cuerpo": [],
                            "estado": "pendiente"
                        })
            for run in paragraph.runs:                              
                # Verificar si el texto está resaltado en amarillo
                if run.font.highlight_color == WD_COLOR_INDEX.YELLOW:
                    if not paragraph.style.name.startswith('Heading 1'):
                        texto_resaltado = run.text
                        # Añadir el párrafo con su índice
                        nota[contador_notas]['cuerpo'].append({
                            'indice': len(nota[contador_notas]['cuerpo']) + 1,
                            'texto': texto_resaltado
                        })                                          
        
        # Guardar las notas en el nuevo documento
        for nota_a_guardar in nota:
            nuevo_doc.add_heading(nota_a_guardar["titulo"], level=1)
            for parrafo in nota_a_guardar["cuerpo"]:
                nuevo_doc.add_paragraph(f"{parrafo['texto']}")                
        
        # Guardar el documento
        nuevo_doc.save(output_path)

        logger.info (f"main.py - extraer_texto_resaltado - 01 - ¡Proceso completado! Texto extraído guardado en: {output_path}")
        return output_path  # Devolver la ruta del archivo guardado
        
    except Heading1NotFoundException as e:
        logger.info (f"main.py - extraer_texto_resaltado - 02 - Error: {str(e)}")
        raise
    except Exception as e:
        logger.info (f"main.py - extraer_texto_resaltado - 03 - Error al procesar el documento: {str(e)}")
        raise

def contar_cantidad_de_palabras(texto):
    """
    Cuenta la cantidad de palabras en un texto dado.
    Args:
        texto (str): El texto en el que se contarán las palabras.
    Returns:
        int: La cantidad de palabras en el texto.
    """
    texto = texto.replace(',', '') # eliminar comas para un conteo más preciso
    texto = texto.replace('.', '') # eliminar puntos para un conteo más preciso
    palabras = texto.split()
    return len(palabras)

def contar_cantidad_de_caracteres(texto):
    """
    Cuenta la cantidad de caracteres en un texto dado.
    Args:
        texto (str): El texto en el que se contarán los caracteres.
    Returns:
        int: La cantidad de caracteres en el texto.
    """
    return len(texto)

def tamanio_archivo_en_megabytes(ruta_archivo):
    """
    Obtiene el tamaño de un archivo en megabytes.
    Args:
        ruta_archivo (str): La ruta al archivo.
    Returns:
        float: El tamaño del archivo en megabytes.
    """
    if os.path.isfile(ruta_archivo):
        tamaño_bytes = os.path.getsize(ruta_archivo)
        tamaño_megabytes = tamaño_bytes / (1024 * 1024)  # Convertir bytes a megabytes
        return tamaño_megabytes
    else:
        raise FileNotFoundError(f"El archivo XML no existe.")

def convertir_a_formato_ssml(input_path,output_path):
    """
    Convierte el texto del documento de salida a formato SSML.
    Args:
        documento_salida (str): Ruta al documento Word de salida (.docx)
    """
    try:
        doc = Document(input_path)
        ssml_output_string = '<?xml version="1.0"?><speak>'
        
        """
        Encabezado: 
            <?xml version="1.0"?>
            <speak>
        Heading 1 formato SSML:
            <voice name="es-US-Standard-B" gender="MALE">
            <prosody rate="medium" volume="loud">
            <emphasis level="strong">

        Cuerpo formato SSML:
            <voice name="es-US-Standard-A" gender="FEMALE">
            <prosody rate="medium" volume="medium">
        """
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading 1'):
                ssml_output_string += f'<voice name="es-US-Standard-B" gender="MALE"><prosody rate="medium" volume="loud"><emphasis level="strong">{paragraph.text}</emphasis></prosody></voice>\n'
            else:
                ssml_output_string += f'<voice name="es-US-Standard-A" gender="FEMALE"><prosody rate="medium" volume="medium">{paragraph.text}</prosody></voice>'

        ssml_output_string += '</speak>'
    
        # Parse the XML string with minidom
        dom = xml.dom.minidom.parseString(ssml_output_string)
        # ssml_output = dom.toxml()
        # If you want to pretty-print the XML
        ssml_output_pretty_xml = dom.toprettyxml(indent="    ")

        cantidad_palabras = contar_cantidad_de_palabras(ssml_output_pretty_xml)
        cantidad_caracteres = contar_cantidad_de_caracteres(ssml_output_pretty_xml)        
        
        # Guardar el SSML en un archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ssml_output_pretty_xml)
            
        logger.info (f"main.py - convertir_a_formato_ssml - 01 - ¡SSML generado y guardado en: {output_path}!")
        return [cantidad_palabras, cantidad_caracteres]
    except Exception as e:
        logger.info (f"main.py - convertir_a_formato_ssml - 02 - Error al convertir a SSML: {str(e)}")
    # Obtener el nombre del archivo del cuerpo de la solicitud
    base_url = "http://localhost:5001/"
    url = base_url + filename
    # filename = request.get_json()['filename']
    file_path = os.path.join(SAVE_FOLDER, filename)

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    response = requests.post(url)

    # return jsonify({'message': 'Audio generated successfully', 'filename': filename}), 200
    return send_file(file_path, as_attachment=True)

@app.route('/api/generar_audio', methods=['GET'])
# @secure_endpoint # Este endpoint solo puede ser llamado desde el frontend
@cross_origin(origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
def generar_audio():
    filename = request.args.get('filename')
    if not filename:
        return "Filename es requerido", 400
    
    url = f"http://api-proxy:5000/api_proxy/generar_audio?filename={filename}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            result = response.json()     
            logger.info(f"main.py - generar_audio - 01 - Generando audio para el archivo: {result[0]}")
            audio_file_input = filename.split('.')[0] + '.wav'
            audio_file_output = filename.split('.')[0] + '.ogg'
            audio_optimizado = optimize_audio(os.path.join(AUDIO_FOLDER,audio_file_input), os.path.join(AUDIO_FOLDER,'optimizado',audio_file_output))

            return send_from_directory(
                directory = AUDIO_FOLDER + 'optimizado/',
                path = audio_file_output, 
                as_attachment=False,
                mimetype='audio/ogg'
            )

        except Exception as e:
            logger.info(f"main.py - generar_audio - 03 - Error procesando audio: {e}")
            return jsonify({"status": "ERROR", "message": f"Error procesando audio: {e}"}), 500
    else:
        logger.info(f"main.py - generar_audio - 04 - Error llamando a api-proxy: {response.status_code}")
        return jsonify({"status": "ERROR", "message": "Error llamando a api-proxy"}), 500

@app.route('/api/compartir_telegram', methods=['POST'])
@cross_origin(origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
def compartir_a_telegram():
    try:
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return jsonify({"status": "ERROR", "message": "Telegram bot token or chat ID not configured"}), 500

        # Obtener el archivo de audio del FormData
        if 'audio_file' not in request.files:
            return jsonify({"status": "ERROR", "message": "No audio file provided"}), 400
        
        audio_file = request.files['audio_file']
        audio_name = request.form.get('name', 'audio.ogg')

        if audio_file.filename == '':
            return jsonify({"status": "ERROR", "message": "No file selected"}), 400

        logger.info(f"main.py - compartir_a_telegram - 01 - Compartiendo audio: {audio_name}")
        logger.info(f"main.py - compartir_a_telegram - 02 - Tipo de archivo: {audio_file.content_type}")

        telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"
        # Preparar los datos para Telegram
        files = {
            'audio': (audio_name, audio_file.stream, 'audio/ogg')
        }

        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': 'Audio generado desde la aplicación',
            'title': audio_name.split('.')[0]  # Nombre sin extensión
        }

        # Enviar a Telegram
        response = requests.post(telegram_api_url, files=files, data=data)

        word_filename = audio_name.split('.')[0] + '.docx'
        file_path = os.path.join(PROCESADOS, word_filename)
        
        with open(file_path, 'rb') as word_file:
            # Preparar los archivos para Telegram - SOLO puedes enviar un archivo por mensaje
            telegram_doc_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            
            files_doc = {
                'document': (word_filename, word_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            data_doc = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': 'Documento generado desde la aplicación',
                'title': audio_name.split('.')[0]  # Nombre sin extensión
            }

            response_doc = requests.post(telegram_doc_url, files=files_doc, data=data_doc)

        if response.status_code == 200:
            logger.info("main.py - compartir_a_telegram - Compartido a Telegram")
            return jsonify({"status": "OK", "message": "Audio compartido en Telegram"}), 200
        else:
            error_msg = f"Error de Telegram: {response.status_code} - {response.text}"
            logger.error(f"main.py - compartir_a_telegram - {error_msg}")
            return jsonify({"status": "ERROR", "message": error_msg}), 500

    except Exception as e:
        logger.error(f"main.py - compartir_a_telegram - Error compartiendo audio en Telegram: {str(e)}")
        return jsonify({"status": "ERROR", "message": f"Error compartiendo audio en Telegram: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    respuesta = {"status": "OK", "message": "API funcionando"}
    logger.info(respuesta)
    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)