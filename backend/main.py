# -*- coding: utf-8 -*-
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import os
import xml.dom.minidom
from flask import Flask, request, jsonify, send_file, send_from_directory
import requests
from flask_cors import CORS, cross_origin  # Importa la extensión CORS
import os
from functools import wraps
from dotenv import load_dotenv
import datetime

import sys
from pydub import AudioSegment

from dataclasses import dataclass
import logging

# Configurar logging para que vaya a stdout (se captura con docker logs)
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

load_dotenv()
# ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

app = Flask(__name__)

# con blueprint, las rutas de telegram se registran automáticamente al importar el blueprint

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

    # logger.info(f"main.py - upload_file - 01 - Nombre del archivo subido: {FILENAME}")
    # Asegurarse de que el directorio existe (por si acaso)
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    file_path = os.path.join(SAVE_FOLDER, file.filename)
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


@app.route('/api/health', methods=['GET'])
def health_check():
    respuesta = {"status": "OK", "message": "API funcionando"}
    logger.info(respuesta)
    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)