import logging
import requests
logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token=None):
        self.session = requests.Session()
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_document(self, chat_id, file_path, caption=""):
        """Envía documento a Telegram"""
        try:
            with open(file_path, 'rb') as file:
                response = self.session.post(
                    f"{self.base_url}/sendDocument",
                    data={
                        'chat_id': chat_id,
                        'caption': caption,
                        'parse_mode': 'HTML'
                    },
                    files={'document': file},
                    timeout=30
                )
                print(f"DEBUG: Respuesta Telegram -> {response}") # Esto saldrá en la consola
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error al enviar documento: {e}")
            return None

        return self._handle_response(response, context="Documento")
    
    def send_audio(self, chat_id, file_path, title="", performer=""):
        """Envía audio a Telegram (reproducible)"""
        try:
            with open(file_path, 'rb') as file:
                response = self.session.post(
                    f"{self.base_url}/sendAudio",
                    data={
                        'chat_id': chat_id,
                        'title': title,
                        'performer': performer,
                        'parse_mode': 'HTML'
                    },
                    files={'audio': file},
                    timeout=30
                )
            return self._handle_response(response, context="Audio") 
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error al enviar audio: {e}")
            return None
    
    def check_health(self):
        """Verifica conexión con Telegram"""
        try:
            response = self.session.get(f"{self.base_url}/getMe", timeout=5)
            response.raise_for_status()
            username = response.json().get('result', {}).get('username')
            print(f"username: {username}")
            return username
        except:
            return None

    def _handle_response(self, response, context="Operación"):
        """Método auxiliar para no repetir lógica de parseo"""
        try:
            response.raise_for_status()
            result = response.json()

            print(f"DEBUG _hanlde_response: Respuesta JSON -> {result['result']['success']}") # Esto saldrá en la consola

            if result['result']['success']:
                logger.info(f"{context} enviado correctamente.")
                return {'success': True, 'message_id': result['result']['message_id']}
            else:
                logger.error(f"Error API Telegram: {result.get('description')}")
                return {'success': False, 'error': result.get('description')}
        except Exception as e:
            logger.error(f"Error procesando respuesta {context}: {e}")
            return {'success': False, 'error': str(e)}

