from google.oauth2 import service_account
from google.auth.transport.requests import Request
from .credentials import GoogleCloudCredentials
from ..exceptions import AuthenticationError

class GoogleCloudAuthenticator:
    """Manejador de autenticación con Google Cloud"""
    
    def __init__(self):
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
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
            if not self.credentials_path:
                raise ValueError(
                    "GOOGLE_APPLICATION_CREDENTIALS no está configurado"
                )
            
            # Convertir a Path para mejor manejo
            creds_file = Path(self.credentials_path)
            
            # Verificar que el archivo existe (está montado)
            if not creds_file.exists():
                raise FileNotFoundError(
                    f"Archivo de credenciales no encontrado: {self.credentials_path}\n"
                    f"Verifica que el volumen está montado en docker-compose.yml"
                )
            
            if not creds_file.is_file():
                raise ValueError(f"No es un archivo: {self.credentials_path}")
            
            # ✅ LEER DESDE ARCHIVO JSON (volumen montado)
            with open(creds_file, 'r') as f:
                credentials_info = json.load(f)
        
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
        # No implementado
        pass
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si está autenticado"""
        return self._client is not None and not self.credentials.expired