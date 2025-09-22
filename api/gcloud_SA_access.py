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
    
