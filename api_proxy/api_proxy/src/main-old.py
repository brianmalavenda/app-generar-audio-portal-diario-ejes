from ..gcloud_tts.client import GoogleCloudTTSClient
from dotenv import load_dotenv
import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  
from ..utils.process_files import leer_docx_completo
from ..utils.validate import validar_procesar
from dataclasses import dataclass
import json
import logging
import sys

# TODA ESTA CONFIGURACION VA AL INIT.PY
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

#
# ACA TENIA LOS ENDPOINTS -> LOS PASAMOS AL ARCHIVO ROUTES
#

if __name__ == '__main__':
    #Dentro de un contenedor, localhost es solo el contenedor mismo. Si quieres que otro contenedor lo vea, Flask debe escuchar en 0.0.0.0 (todas las interfaces de red).
    app.run(host='0.0.0.0', port=5000, debug=True)