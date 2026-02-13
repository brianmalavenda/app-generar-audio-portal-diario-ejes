import os
from flask import request, jsonify, Blueprint, current_app
import requests
import logging
from .client import TelegramService 
from dotenv import load_dotenv

logger = logging.getLogger(__name__) 
telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')

load_dotenv()

# Inicializar servicio
def get_client():
    """
    Obtiene una instancia del servicio solo si el token está configurado.
    Esto evita que la app falle al iniciar si falta la config.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    print(f"DEBUG: Token encontrado -> {token}") # Esto saldrá en la consola
    if not token:
        logger.warning("Intento de uso de Telegram sin TELEGRAM_BOT_TOKEN configurado")
        return None
    
    return TelegramService(token)

@telegram_bp.route('/health', methods=['GET'])
def health_check():
    service = get_client()
    if not service:
        return jsonify({"status": "unhealthy", "error": "Token no configurado"}), 503
    
    bot_user = service.check_health()
    if bot_user:
        return jsonify({"status": "healthy", "bot_username": bot_user})
    
    return jsonify({"status": "unhealthy", "error": "No se pudo conectar a Telegram API"}), 503

@telegram_bp.route('/share', methods=['POST'])
def share_file():
    service = get_client()
    if not service:
        return jsonify({"success": False, "error": "Servicio de Telegram no configurado en el servidor"}), 500

    data = request.json
    chat_id = data.get('chatId')
    file_name = data.get('fileName')
    audio_file_name = data.get('audioFileName')

    if not chat_id:
        return jsonify({"success": False, "error": "chatId requerido"}), 400

    # Usamos current_app.config para las rutas (Buena Práctica)
    base_path = current_app.config.get('SAVE_FOLDER', '/app/shared-files')
    
    # Construcción de rutas dinámica según la estructura que mencionaste antes
    # Asumiendo que 'SAVE_FOLDER' apunta a /app/shared-files/diario_pintado o similar
    # O construimos la ruta completa:
    shared_root = os.path.dirname(base_path) # Sube un nivel si es necesario, o usa config directa
    
    results = {}
    
    # Lógica de envío de documento
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

    # Determinar éxito general
    any_success = any(r.get('success') for r in results.values() if isinstance(r, dict))
    
    status_code = 200 if any_success else 400
    return jsonify({
        "success": any_success,
        "results": results
    }), status_code