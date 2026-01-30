from google.oauth2 import service_account
from google.auth.transport.requests import Request
# from .credentials import GoogleCloudCredentials
from ..exceptions import AuthenticationError

class GoogleCloudAuthenticator:
    """Manejador de autenticación con Google Cloud"""
    
    def __init__(self):
        # self.credentials = credentials
        self.credentials = None
        self._client = None
    
    def authenticate_old(self) -> service_account.Credentials:
        """Autentica y retorna las credenciales"""
        try:
            if self.credentials.credentials_file:
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials.credentials_file,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            elif self.credentials.token:
                # Lógica para usar token existente
                creds = self._authenticate_with_token()
            else:
                # Intentar autenticación por ADC (Application Default Credentials)
                creds, _ = google.auth.default()
            
            # Refrescar token si es necesario
            if creds.expired:
                creds.refresh(Request())
            
            self._client = creds
            return creds
            
        except Exception as e:
            raise AuthenticationError(f"Error de autenticación: {str(e)}")
    
    def authenticate(self) -> service_account.Credentials:
        """Obtiene token usando Service Account"""
        try:
            # Leer credenciales desde variable de entorno
            credentials_json = os.getenv('GOOGLE_TTS_API_KEY')

            if credentials_json:
                # Si las credenciales están en una variable de entorno
                credentials_info = json.loads(credentials_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )

            if self.credentials.expired:
                self.credentials.refresh(google.auth.transport.requests.Request())
                self.client = self.credentials.token

            return self.credentials

        # DEUDA TECNICA: Manejar logs unificados en paquete de logging
        # except Exception as e:
        #     logger.info(f"api-proxy - gcloud_SA_access.py - get_access_token_service_account - 01 - Error obteniendo token de servicio: {e}")
        #     return None
        except Exception as e:
            raise AuthenticationError(f"Error de autenticación: {str(e)}")
    
    def _authenticate_with_token(self) -> service_account.Credentials:
        """Autenticación con token (implementación básica)"""
        # Implementar según tus necesidades
        pass
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si está autenticado"""
        return self._client is not None and not self.credentials.expired