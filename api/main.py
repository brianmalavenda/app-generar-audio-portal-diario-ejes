from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException, status, request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from gcloud_SA_access import get_access_token, get_project_id, synthesize_speech

load_dotenv()
API_URL = os.getenv("API_URL")
TEST_TOKEN = os.getenv("TEST_TOKEN")
# Configuración de seguridad
security = HTTPBearer()
# Modelo de entrada (ajústalo según lo que envíes a Google TTS)
class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "es-US-Standard-A"  # ejemplo
    ssml: bool = False

app = FastAPI(title="Mi API Intermedia para Google TTS")


@app.route('/api-proxy/getaudio', methods=['GET'])
def get_audio():
    filename = request.args.get('filename')
    if not filename:
        return "Filename es requerido", 400
    
    # Ruta corregida
    path_salida = "/app/shared-files/diario_ssml/"
    documento_salida = os.path.join(path_salida, filename)
    
    try:
        with open(documento_salida, "r", encoding="utf-8") as file:
            text_ssml = file.read()
            print("Contenido SSML leído correctamente")
    except Exception as e:
        print(f"Error leyendo archivo SSML: {e}")
        return f"Error leyendo archivo: {e}", 500

    # Usar la autenticación por service account
    token = get_access_token_service_account()
    project_id = get_project_id_service_account()
    
    if not token or not project_id:
        return "Error de autenticación con Google Cloud", 500

    result = synthesize_speech(text_ssml)
    
    if result and 'audioContent' in result:
        try:
            import base64
            audio_data = base64.b64decode(result['audioContent'])
            
            # Crear nombre de archivo para el audio
            audio_filename = f"audio_{os.path.splitext(filename)[0]}.ogg"
            audio_path = os.path.join("/app/shared-files/diario_pintado/", audio_filename)
            
            # Guardar archivo de audio
            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_data)
            print(f"Audio guardado en: {audio_path}")
            
            # Devolver el archivo de audio
            return send_file(audio_path, as_attachment=True, download_name=audio_filename)
            
        except Exception as e:
            print(f"Error procesando audio: {e}")
            return f"Error procesando audio: {e}", 500
    else:
        print("Error en la síntesis de voz")
        return "Error en la síntesis de voz", 500
    
@app.get("/")
def read_root():
    return {"message": "API Intermedia de TTS - Usa /synthesize con Bearer Token"}