import os
import json
from google.oauth2 import service_account
import google.auth.transport.requests
from google.cloud import texttospeech, storage
import datetime
import requests
from dataclasses import dataclass
import time
import logging
import sys

# Configurar logging para que vaya a stdout (se captura con docker logs)
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    name: str = "test"
    content: str = None
    is_long: bool = False   

@dataclass
class GoogleCloud:
    project_id: str = ""
    token: str = ""


def get_access_token_service_account():
    """Obtiene token usando Service Account (mejor para Docker)"""
    try:
        # Leer credenciales desde variable de entorno
        credentials_json = os.getenv('GOOGLE_TTS_API_KEY')

        if credentials_json:
            # Si las credenciales están en una variable de entorno
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
      
        # Obtener token
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    
    except Exception as e:
        logger.info(f"api-proxy - gcloud_SA_access.py - get_access_token_service_account - 01 - Error obteniendo token de servicio: {e}")
        return None

def get_project_id_service_account():
    """Obtiene project ID desde las credenciales de servicio"""
    try:
        credentials_json = os.getenv('GOOGLE_TTS_API_KEY')
        
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            return credentials_info.get('project_id')
    
    except Exception as e:
        logger.info(f"api-proxy - gcloud_SA_access.py - get_project_id_service_account - 01 - Error obteniendo project ID: {e}")
        return None

def make_audio_public(bucket_name, audio_filename):
    """Hace público un archivo de audio ya existente en el bucket"""
    credentials = get_access_token_service_account
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    # Especificar el blob (archivo) dentro del bucket
    blob = bucket.blob(audio_filename)
    
    # Hacer el archivo público
    blob.make_public()
    
    # Obtener URL pública
    public_url = blob.public_url
    
    logger.info(f"✅ Audio hecho público: {public_url}")
    return public_url

def generate_signed_url(bucket_name, audio_filename, expiration_hours=24):
    """Genera una URL firmada temporal para el archivo"""
    try:
        logger.info(f"🔐 Generando URL firmada para: {audio_filename}")
        
        # Obtener credenciales
        credentials_json = os.getenv('GOOGLE_TTS_API_KEY')
        if not credentials_json:
            logger.error("❌ GOOGLE_TTS_API_KEY no encontrada")
            return None
        
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Crear cliente de Storage
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(audio_filename)
        
        # Verificar si el archivo existe
        if not blob.exists():
            logger.error(f"❌ Archivo {audio_filename} no existe")
            return None
        
        # Generar URL firmada (válida por 24 horas por defecto)
        signed_url = blob.generate_signed_url(
            expiration=datetime.timedelta(hours=expiration_hours),
            method='GET'
        )

        logger.info(f"✅ URL firmada generada (válida por {expiration_hours} horas)")
        return signed_url
        
    except Exception as e:
        logger.error(f"❌ Error generando URL firmada: {str(e)}")
        return None

def synthesize_speech(gcloud: GoogleCloud, file: FileInfo):
    bucket_name = "audios-text-to-speech-01"
    destino_local = "/app/shared-files/audio"

    if not gcloud.token:
        return None

    if file.is_long:
        url = f"https://texttospeech.googleapis.com/v1beta1/projects/{gcloud.project_id}/locations/global:synthesizeLongAudio"
        audio_encoding = "LINEAR16"  # Único soportado para audio largo
        extension = ".wav" # No soporta el formato OGG_OPUS
    else:
        print("############# Audio corto")
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        audio_encoding = "MP3"  # Puedes usar MP3, OGG_OPUS, etc.
        extension = ".mp3"

    headers = {
        "Authorization": f"Bearer {gcloud.token}",
        "x-goog-user-project": gcloud.project_id,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "input": {
            # "ssml": text
            "text": file.content
        },
        "voice": {
            "language_code": "es-us",
            "name": "es-US-Standard-A"
        },
        "audio_config": {
            "audio_encoding": audio_encoding,
            "speaking_rate": 1.0
        }
    }
    
    # Si el audio es largo tengo que agregar al cuerpo del POST la URI del bucket
    if file.is_long:
        data["output_gcs_uri"] = f"gs://{bucket_name}/{file.name}{extension}"

    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - 01 - Respuesta de la api de grabacion de audio {response.json()}")

    # Crear nombre de archivo para el audio
    audio_filename = f"{file.name}{extension}"
    print(f"Este es el archivo de audio {audio_filename}")
    audio_path = os.path.join(destino_local, audio_filename)
    logger.info(f"file.is_long: {file.is_long}")

    # Si es audio corto, retornar inmediatamente
    if not file.is_long:
        if response.status_code == 200:
            if response and 'audioContent' in response:
                try:
                    import base64
                    audio_data = base64.b64decode(response['audioContent'])
                    os.makedirs(destino_local, exist_ok=True)

                    # Guardar archivo de audio
                    with open(audio_path, "wb") as audio_file:
                        audio_file.write(audio_data)
                    
                    public_url = make_audio_public(bucket_name, f"{audio_filename}")
                    logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - make_audio_public - 02 - Audio guardado en: {public_url}")
                    
                    return {
                        "status": "success",
                        "size_audio":"short",
                        "codigo":"001",
                        "respuesta": response.text,
                        "public_url": public_url
                    }
                except Exception as e:
                    logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - 03 - Error guardando audio corto: {e}")
                    return f"Error guardando audio corto: {e}", 500
        else:
            return {
                "estado": "error",
                "size_audio":"short",
                "codigo":"002",
                "respuesta": response.text
            }

    # Si el audio es largo
    operation = response.json()["name"]
    logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - XXX - Operación iniciada: {operation}, respuesta: {response.text}")  
    operation_url = f"https://texttospeech.googleapis.com/v1beta1/{operation}"
    
    start_time = time.time()
    timeout_minutes = 30
    timeout_seconds = timeout_minutes * 60
    vueltas = 0

    while True:
        # Verificar timeout
        if time.time() - start_time > timeout_seconds:
            return {
                "estado": "timeout",
                "size_audio":"large",
                "codigo":"003",
                "respuesta": f"Error - La operación excedió el tiempo límite de {timeout_minutes} minutos"
            }

        logger.info(f"Vuelta numero: {vueltas + 1}")    
        # Esperar antes de consultar
        time.sleep(10)
        # Consultar estado de la operación
        op_response = requests.get(operation_url, headers=headers)
        
        if op_response.status_code != 200:
            return {
                "estado": "error",
                "size_audio":"large",
                "codigo":"004",
                "respuesta": f"Error consultando operación: {op_response.text}"
            }
        
        operation_data = op_response.json()
        logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - 04 - Estado de operación: {operation_data}")
        done = operation_data.get("done", False)
        
        # Verificar si terminó
        if done:
            logger.info("✅ Operación completada")
            if "error" in operation_data: 
                return {
                    "estado": "error",
                    "size_audio":"large",
                    "codigo":"005",
                    "respuesta": operation_data["error"].get("message", "Error desconocido")                    
                }
            else:
                # en audio_path mando toda la ruta incluido el nombre del archivo
                time.sleep(10)
                # tengo que descargar el audio desde GCS porque necesito tener el archivo en el servidor para reenviarlo a telegram
                # public_url = make_audio_public(bucket_name, f"{audio_filename}")
                descargar_audio_gs(gcloud, bucket_name, f"{file.name}{extension}", audio_path)
                logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - 05 - {operation_data} -----------")
                # public_signed_url = generate_signed_url(bucket_name, f"{file.name}{extension}", expiration_hours=24)
                
                return {
                    "status": "success",
                    "size_audio":"large",
                    "codigo":"006",
                    "respuesta": response.text
                    # "public_url": public_signed_url
                }

        
        # Mostrar progreso
        # metadata = operation_data.get("metadata", {})
        # progress = metadata.get("progressPercentage", 0)
        # logger.info(f"api-proxy - gcloud_SA_access.py - synthesize_speech - 06 - 📊 Progreso: {progress}%")

def descargar_audio_gs(gcloud, bucket_name, audio_name, destino_local):
    """
    Descarga un audio desde Google Cloud Storage
    
    Args:
        gcloud: Objeto con token y project_id
        bucket_name: Nombre del bucket (audios-text-to-speech-01)
        audio_name: Nombre del archivo en el bucket (audio_test_01.mp3)
        destino_local: Ruta local donde guardar el archivo
    """
    
    # URL de la API de Google Cloud Storage
    url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/{audio_name}?alt=media"
    
    headers = {
        "Authorization": f"Bearer {gcloud.token}",
        "x-goog-user-project": gcloud.project_id
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code == 200:
            # Asegurar que el directorio destino existe
            os.makedirs(os.path.dirname(destino_local), exist_ok=True)
            
            # Guardar el archivo
            with open(destino_local, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"api-proxy - gcloud_SA_access.py - descargar_audio_gs - 01 - ✅ Audio descargado exitosamente: {destino_local}")
            return True
        else:
            logger.info(f"api-proxy - gcloud_SA_access.py - descargar_audio_gs - 02 - ❌ Error descargando audio: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.info(f"api-proxy - gcloud_SA_access.py - descargar_audio_gs - 03 - ❌ Error en descarga: {e}")
        return False

def monitorear_operacion_hasta_terminar(gcloud_session, operation_name, access_token, bucket_name, audio_filename):
    """Monitorea hasta que la operación termine REALMENTE"""
    
    operation_url = f"https://texttospeech.googleapis.com/v1/{operation_name}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    timeout_segundos = 10 * 60  # 10 minutos
    
    while time.time() - start_time < timeout_segundos:
        try:
            response = gcloud_session.get(operation_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                time.sleep(10)
                continue
            
            operation_data = response.json()
            done = operation_data.get('done', False)
            progress = operation_data.get('metadata', {}).get('progressPercentage', 0)
            
            logger.info(f"📊 Progreso: {progress}% - Terminado: {done}")
            
            if done:
                logger.info("✅ Operación COMPLETADA realmente")
                
                if operation_data.get('error'):
                    error_msg = operation_data['error'].get('message', 'Error desconocido')
                    return {"status": "error", "message": f"Error en síntesis: {error_msg}"}
                
                # ✅ ESPERAR un poco más para asegurar que el archivo esté en Storage
                logger.info("⏳ Esperando que el archivo esté disponible en Storage...")
                time.sleep(10)  # Esperar 10 segundos adicionales
                
                # ✅ AHORA SÍ generar la URL firmada
                signed_url = generate_signed_url(bucket_name, audio_filename)
                
                if signed_url:
                    return {
                        "status": "success",
                        "message": "Audio generado correctamente",
                        "public_url": signed_url,
                        "audio_filename": audio_filename
                    }
                else:
                    return {"status": "error", "message": "No se pudo generar URL accesible"}
            
            time.sleep(10)  # Esperar 10 segundos entre consultas
            
        except Exception as e:
            logger.error(f"Error monitoreando: {str(e)}")
            time.sleep(10)
            continue
    
    return {"status": "error", "message": "Timeout en la síntesis"}