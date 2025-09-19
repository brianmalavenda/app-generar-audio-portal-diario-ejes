import requests
import subprocess
import json
from dotenv import load_dotenv
import os

def get_access_token():
    """Obtiene el token de acceso usando gcloud auth print-access-token"""
    try:
        # el comando subprocess.check_output ejecuta el comando en la terminal y captura la salida
        token = subprocess.check_output(['gcloud', 'auth', 'print-access-token'], text=True).strip()
        return token
    except subprocess.CalledProcessError as e:
        print(f"Error obteniendo token de acceso: {e}")
        return None
    

def get_project_id():
    """Obtiene el ID del proyecto usando gcloud config get-value project"""
    try:
        project_id = subprocess.check_output(['gcloud', 'config', 'get-value', 'project'], text=True).strip()
        return project_id
    except subprocess.CalledProcessError as e:
        print(f"Error obteniendo el ID del proyecto: {e}")
        return None

def synthesize_speech(text):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    token = get_access_token()
    project_id = get_project_id()

    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-user-project": project_id,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "input": {
            "ssml": text
        },
        "voice": {
            "languageCode": "es-US"
        },
        "audioConfig": {
            "audioEncoding": "ogg_opus",
            "speakingRate": 1.0
        }
    }
    
    try:
        # json.dumps convierte el diccionario data a una cadena JSON
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Después de la línea response = requests.post(...)
        if response.status_code != 200:
            print(f"Error {response.status_code}")
            try:
                # .json() intenta parsear la respuesta como JSON
                error_details = response.json()
                print("Detalles del error:")
                print(json.dumps(error_details, indent=2))
                # raise_for_status() lanza una excepción para códigos de estado HTTP 4xx/5xx
                response.raise_for_status()  
            except:
                print("No se pudo parsear la respuesta como JSON")
                print("Respuesta completa:")
                print(response.text)
                
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return None

# Uso del script
# if __name__ == "__main__": # esto asegura que el código solo se ejecute cuando el script es ejecutado directamente
#     # obtener el texto a partir de un archivo SSML
#     path_salida = "app/shared_file/diario_ssml/"
#     documento_salida = path_salida + "250911RT-SPK_resaltado.docx"

#     try:
#         with open("texto-ssml.xml", "r", encoding="utf-8") as file:
#             TEXT = file.read()
#             print("Contenido SSML leído:")
#             print(TEXT)
#     except Exception as e:
#         print(f"Error leyendo archivo XML: {e}")
#         exit(1)

#     result = synthesize_speech(TEXT)
    
#     if result and 'audioContent' in result:
#         # Decodificar el contenido base64 y guardar como MP3
#         import base64
#         audio_data = base64.b64decode(result['audioContent'])
#         with open("test03-ssml-to-speech.ogg", "wb") as audio_file:
#             audio_file.write(audio_data)
#         print("Audio guardado en formato .ogg")
#     else:
#         print("Error en la síntesis de voz")