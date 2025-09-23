import os
import json
from google.oauth2 import service_account
import google.auth.transport.requests

def get_access_token_service_account():
    """Obtiene token usando Service Account (mejor para Docker)"""
    try:
        # Leer credenciales desde variable de entorno
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        
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
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            return credentials_info.get('project_id')
    
    except Exception as e:
        print(f"Error obteniendo project ID: {e}")
        return None
    

def synthesize_speech(text, token, project_id):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"

    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-user-project": project_id,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "input": {
            "ssml": text
        },
        "voice": {
            "languageCode": "es-US"
        },
        "audioConfig": {
            "audioEncoding": "ogg_opus",
            "speakingRate": 1.0
        }
    }
    
    try:
        # json.dumps convierte el diccionario data a una cadena JSON
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Después de la línea response = requests.post(...)
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            try:
                # .json() intenta parsear la respuesta como JSON
                error_details = response.json()
                print("Detalles del error:")
                print(json.dumps(error_details, indent=2))
                # raise_for_status() lanza una excepción para códigos de estado HTTP 4xx/5xx
                response.raise_for_status()  
            except:
                print("No se pudo parsear la respuesta como JSON")
                print("Respuesta completa:")
                print(response.text)
                
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return None