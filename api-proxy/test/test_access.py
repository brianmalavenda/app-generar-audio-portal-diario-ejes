import os
import json
from google.oauth2 import service_account
import google.auth.transport.requests

def get_access_token_service_account():
    """Obtiene token usando Service Account DESARROLLO"""
    try:
        # Intentar cargar desde archivo (para desarrollo local)
        credentials = service_account.Credentials.from_service_account_file(
            '../cred/key.json',
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
        # Intentar desde archivo
        with open('../cred/key.json', 'r') as f:
            credentials_info = json.load(f)
            return credentials_info.get('project_id')
    
    except Exception as e:
        print(f"Error obteniendo project ID: {e}")
        return None
    
