import os
import json
from google.oauth2 import service_account
import google.auth.transport.requests
from google.cloud import texttospeech
import requests
from dataclasses import dataclass
import time
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
        print(f"Error obteniendo token de servicio: {e}")
        return None

def get_project_id_service_account():
    """Obtiene project ID desde las credenciales de servicio"""
    try:
        credentials_json = os.getenv('GOOGLE_TTS_API_KEY')
        
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            return credentials_info.get('project_id')
    
    except Exception as e:
        print(f"Error obteniendo project ID: {e}")
        return None
    

def synthesize_speech(gcloud: GoogleCloud, file: FileInfo):
    bucket_name = "audios-text-to-speech-01"
    destino_local = "/app/shared-files/audio"

    if not gcloud.token:
        return None

    if file.is_long:
        url = f"https://texttospeech.googleapis.com/v1beta1/projects/{gcloud.project_id}/locations/global:synthesizeLongAudio"
        audio_encoding = "LINEAR16"  # Único soportado para audio largo
        extension = ".wav"
    else:
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        audio_encoding = "OGG_OPUS"  # Puedes usar MP3, OGG_OPUS, etc.
        extension = ".ogg"

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
        data["output_gcs_uri"] = f"gs://audios-text-to-speech-01/{file.name}{extension}"

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Respuesta de la api de grabacion de audio {response.json()}")

    # Crear nombre de archivo para el audio
    audio_filename = f"{file.name}.{extension}"
    print(f"Este es el archivo de audio {audio_filename}")
    audio_path = os.path.join(destino_local, audio_filename)
    
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
                    
                    print(f"Audio guardado en: {audio_path}")
                    
                    return {
                        "estado": "success",
                        "audio_tipo":"short",
                        "codigo":"001",
                        "respuesta": response.json()
                    }
                except Exception as e:
                    print(f"Error guardando audio corto: {e}")
                    return f"Error guardando audio corto: {e}", 500
        else:
            return {
                "estado": "error",
                "audio_tipo":"short",
                "codigo":"002",
                "respuesta": response.text
            }

    # Si el audio es largo
    operation = response.json()["name"]
    operation_url = f"https://texttospeech.googleapis.com/v1beta1/{operation}"
    
    start_time = time.time()
    timeout_minutes = 30
    timeout_seconds = timeout_minutes * 60

    while True:
        # Verificar timeout
        if time.time() - start_time > timeout_seconds:
            return {
                "estado": "timeout",
                "audio_tipo":"large",
                "codigo":"003",
                "respuesta": f"Error - La operación excedió el tiempo límite de {timeout_minutes} minutos"
            }
        
        # Esperar antes de consultar
        time.sleep(10)
        
        # Consultar estado de la operación
        op_response = requests.get(operation_url, headers=headers)
        
        if op_response.status_code != 200:
            return {
                "estado": "error",
                "audio_tipo":"large",
                "codigo":"004",
                "respuesta": f"Error consultando operación: {op_response.text}"
            }
        
        operation_data = op_response.json()
        print(f"Estado de operación: {operation_data}")
        
        # Verificar si terminó
        if operation_data.get("done", False):
            if "error" in operation_data: 
                return {
                    "estado": "error",
                    "audio_tipo":"large",
                    "codigo":"005",
                    "respuesta": operation_data["error"].get("message", "Error desconocido")                    
                }
        else:
            # en audio_path mando toda la ruta incluido el nombre del archivo
            descargar_audio_gs(gcloud, bucket_name, f"{file.name}{extension}", audio_path)
            print(f"------------descargamos audio largo-----------")
            return {
                "estado": "success",
                "audio_tipo":"large",
                "codigo":"006",
                "respuesta": operation_data.get("response", {})
            }
        
        # Mostrar progreso
        metadata = operation_data.get("metadata", {})
        progress = metadata.get("progressPercentage", 0)
        print(f"📊 Progreso: {progress}%")

def descargar_audio_gs(gcloud, bucket_name, audio_name, destino_local):
    """
    Descarga un audio desde Google Cloud Storage
    
    Args:
        gcloud: Objeto con token y project_id
        bucket_name: Nombre del bucket (audios-text-to-speech-01)
        audio_name: Nombre del archivo en el bucket (audio_test_01.wav)
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
            
            print(f"✅ Audio descargado exitosamente: {destino_local}")
            return True
        else:
            print(f"❌ Error descargando audio: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en descarga: {e}")
        return False