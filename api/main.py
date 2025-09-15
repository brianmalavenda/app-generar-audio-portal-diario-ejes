from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

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

# Función para verificar el token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TEST_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Endpoint protegido
@app.post("/synthesize")
async def synthesize_speech(
    request: TextToSpeechRequest,
    token: str = Depends(verify_token)
):
    # Aquí iría tu lógica: transformar a SSML, llamar a Google TTS, etc.
    # Por ahora, solo simulamos una respuesta.

    simulated_response = {
        "message": "Texto recibido y listo para sintetizar",
        "text": request.text,
        "voice": request.voice,
        "ssml_enabled": request.ssml,
        "token_used": token[:10] + "..."  # Solo para demo, no expongas tokens reales
    }

    # Aquí podrías llamar a Google TTS API con tu clave privada (guardada en variables de entorno)
    # y devolver el audio o la URL del audio generado.

    return simulated_response

# Endpoint de prueba sin autenticación
@app.get("/")
def read_root():
    return {"message": "API Intermedia de TTS - Usa /synthesize con Bearer Token"}
