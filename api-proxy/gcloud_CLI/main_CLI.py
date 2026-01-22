from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException, status, request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from connect_gc_cli import get_access_token, get_project_id, synthesize_speech


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
    # obtener el texto a partir de un archivo SSML
    path_salida = "app/shared_file/diario_ssml/"
    documento_salida = os.path.join(path_salida, filename)
    try:
        with open(documento_salida, "r", encoding="utf-8") as file:
            TEXT = file.read()
            print("Contenido SSML leído:")
            print(TEXT)
    except Exception as e:
        print(f"Error leyendo archivo XML: {e}")
        exit(1)

    token = get_access_token()
    project_id = get_project_id()
    result = ''

    if token and project_id:
        result = synthesize_speech(TEXT)
        if result and 'audioContent' in result:
            # Decodificar el contenido base64 y guardar como MP3
            import base64
            audio_data = base64.b64decode(result['audioContent'])
            with open("test03-ssml-to-speech.ogg", "wb") as audio_file:
                audio_file.write(audio_data)
            print("Audio guardado en formato .ogg")
        else:
            print("Error en la síntesis de voz")
    

    return send_file(file_path, as_attachment=True)    

# Función para verificar el token
# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     if credentials.credentials != TEST_TOKEN:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token inválido o no proporcionado",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return credentials.credentials

# Endpoint protegido
# @app.post("/synthesize")
# async def synthesize_speech(
#     request: TextToSpeechRequest,
#     token: str = Depends(verify_token)
# ):
#     # Aquí iría tu lógica: transformar a SSML, llamar a Google TTS, etc.
#     # Por ahora, solo simulamos una respuesta.

#     simulated_response = {
#         "message": "Texto recibido y listo para sintetizar",
#         "text": request.text,
#         "voice": request.voice,
#         "ssml_enabled": request.ssml,
#         "token_used": token[:10] + "..."  # Solo para demo, no expongas tokens reales
#     }

#     # Aquí podrías llamar a Google TTS API con tu clave privada (guardada en variables de entorno)
#     # y devolver el audio o la URL del audio generado.

#     return simulated_response

# Endpoint de prueba sin autenticación
@app.get("/")
def read_root():
    return {"message": "API Intermedia de TTS - Usa /synthesize con Bearer Token"}
