from google.oauth2 import service_account
from google.auth.transport.requests import Request
from .credentials import GoogleCloudCredentials
from ..exceptions import AuthenticationError
from pathlib import Path
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleCloudAuthenticator:
    """Manejador de autenticación con Google Cloud"""
    
    def __init__(self):
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.credentials = None
        self._client = None
    
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
        
            logger.info(f"api-proxy - gcloud_authenticator.py - authenticate - 01 - Cargando credenciales desde {self.credentials_path}")
            logger.info(f"api-proxy - gcloud_authenticator.py - authenticate - 02 - Credenciales cargadas: \n {credentials_info}")

            # self.credentials = service_account.Credentials.from_service_account_info(
            #     credentials_info,
            #     scopes=['https://www.googleapis.com/auth/cloud-platform']
            # )

            self.credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )

            # if self.credentials.expired:
            #     self.credentials.refresh(google.auth.transport.requests.Request())
            #     self.client = self.credentials.token

            # return self.credentials
            if self.credentials.valid:
                logger.info(f"Autenticación exitosa. Cuenta: {self.credentials.service_account_email}")
                self.client = self.credentials.token
                return self.credentials
            else:
                logger.warning("Las credenciales no son válidas")
                return None

        # DEUDA TECNICA: Manejar logs unificados en paquete de logging
        # except Exception as e:
        #     # raise AuthenticationError(f"Error de autenticación: {str(e)}")
        #     logger.info(f"api-proxy - gcloud_authenticator.py - authenticate - 02 - Error obteniendo credenciales: {e}")
        #     return None
        except json.JSONDecodeError as e:
            logger.error(f"Error en formato JSON: {e}")
        except ValueError as e:
            logger.error(f"Error en credenciales: {e}")
        except Exception as e:
            logger.error(f"Error inesperado en autenticación: {e}", exc_info=True)
        
        return None
    
    def get_token(self):
        """Obtener token de acceso"""
        if not self.credentials:
            if not self.authenticate():
                return None
        
        # Refrescar si es necesario
        if self.credentials.expired:
            try:
                self.credentials.refresh(google.auth.transport.requests.Request())
            except Exception as e:
                logger.error(f"Error refrescando token: {e}")
                return None
        
        return self.credentials.token

    def _authenticate_with_token(self) -> service_account.Credentials:
        """Autenticación con token (implementación básica)"""
        # No implementado
        pass
    
    @property
    def is_authenticated(self) -> bool:
        """Verifica si está autenticado"""
        return self._client is not None and not self.credentials.expired