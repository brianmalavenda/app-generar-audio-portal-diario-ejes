import os
import requests
from flask import Blueprint, request, jsonify
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')

load_dotenv()

class TelegramService:
    def __init__(self, token=None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN no configurado")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_document(self, chat_id, file_path, caption=""):
        """Envía documento a Telegram"""
        try:
            with open(file_path, 'rb') as file:
                response = requests.post(
                    f"{self.base_url}/sendDocument",
                    data={
                        'chat_id': chat_id,
                        'caption': caption,
                        'parse_mode': 'HTML'
                    },
                    files={'document': file},
                    timeout=30
                )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Documento enviado: {os.path.basename(file_path)}")
                return {
                    'success': True,
                    'message_id': result['result']['message_id'],
                    'file_name': result['result']['document']['file_name']
                }
            else:
                logger.error(f"Telegram API error: {result}")
                return {'success': False, 'error': result.get('description')}
                
        except Exception as e:
            logger.error(f"Error enviando documento: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_audio(self, chat_id, file_path, title="", performer=""):
        """Envía audio a Telegram (reproducible)"""
        try:
            with open(file_path, 'rb') as file:
                response = requests.post(
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
            
            response.raise_for_status()
            return {'success': True, 'message_id': response.json()['result']['message_id']}
            
        except Exception as e:
            logger.error(f"Error enviando audio: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_multiple(self, chat_id, document_path=None, audio_path=None, text=""):
        """Envía múltiples archivos"""
        results = {}
        
        if text:
            # Enviar texto primero
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    'chat_id': chat_id,
                    'text': f"📝 <b>Contenido:</b>\n\n{text[:1000]}...",
                    'parse_mode': 'HTML'
                }
            )
            results['text_message_id'] = response.json()['result']['message_id']
        
        if document_path and os.path.exists(document_path):
            results['document'] = self.send_document(
                chat_id, 
                document_path, 
                caption="📄 <b>Documento original</b>"
            )
        
        if audio_path and os.path.exists(audio_path):
            audio_name = os.path.basename(audio_path).rsplit('.', 1)[0]
            results['audio'] = self.send_audio(
                chat_id,
                audio_path,
                title=audio_name,
                performer="Audio App"
            )
        
        return results


# Inicializar servicio
telegram_service = TelegramService()

@telegram_bp.route('/share', methods=['POST'])
def share_file():
    """Endpoint para compartir archivos"""
    try:
        data = request.json
        chat_id = data.get('chatId')
        file_name = data.get('fileName')
        audio_file_name = data.get('audioFileName')
        
        if not chat_id:
            return jsonify({"success": False, "error": "chatId requerido"}), 400
        
        base_path = "/app/shared-files"
        results = {}
        
        # Enviar documento si se especificó
        if file_name:
            doc_path = os.path.join(base_path, "diario_pintado", file_name)
            if os.path.exists(doc_path):
                results['document'] = telegram_service.send_document(
                    chat_id, 
                    doc_path, 
                    caption=f"📄 <b>{file_name}</b>"
                )
            else:
                results['document'] = {'success': False, 'error': 'Documento no encontrado', 'filename' : file_name, 'doc_path': doc_path}
        
        # Enviar audio si se especificó
        if audio_file_name:
            audio_path = os.path.join(base_path, "audio",  audio_file_name + ".mp3")
            if os.path.exists(audio_path):
                audio_name = audio_file_name.rsplit('.', 1)[0]
                results['audio'] = telegram_service.send_audio(
                    chat_id,
                    audio_path,
                    title=audio_name,
                    performer="Audio App"
                )
            else:
                results['audio'] = {'success': False, 'error': 'Audio no encontrado', 'audioname' : audio_file_name, 'doc_path': audio_path}
        
        # Verificar si algún envío fue exitoso
        any_success = any(r.get('success') for r in results.values() if isinstance(r, dict))
        
        return jsonify({
            "success": any_success,
            "results": results,
            "message": "Archivos procesados" if any_success else "Error enviando archivos"
        })
        
    except Exception as e:
        logger.error(f"Error en endpoint /share: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@telegram_bp.route('/health', methods=['GET'])
def health_check():
    """Health check para Telegram service"""
    try:
        # Probar conexión con Telegram API
        response = requests.get(f"{telegram_service.base_url}/getMe", timeout=5)
        bot_info = response.json()
        
        return jsonify({
            "status": "healthy",
            "bot_username": bot_info.get('result', {}).get('username'),
            "service": "telegram-file-share"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503