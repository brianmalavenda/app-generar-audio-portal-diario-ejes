import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
import google.auth.transport.requests

load_dotenv('.env')

def get_access_token_service_account():
    """Obtiene token usando Service Account (mejor para Docker)"""
    try:
        # acceso a la variable GOOGLE_TTS_API_KEY del archivo .env
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
        print(f"token: {credentials.token}")
        return credentials.token
    
    except Exception as e:
        print(f"api-proxy - gcloud_SA_access.py - get_access_token_service_account - 01 - Error obteniendo token de servicio: {e}")
        return None

def get_project_id_service_account():
    """Obtiene project ID desde las credenciales de servicio"""
    try:
        credentials_json = os.getenv('GOOGLE_TTS_API_KEY')
        
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            print(f"project_ide: {credentials_info.get('project_id')}")
            return credentials_info.get('project_id')
    
    except Exception as e:
        logger.info(f"api-proxy - gcloud_SA_access.py - get_project_id_service_account - 01 - Error obteniendo project ID: {e}")
        return None