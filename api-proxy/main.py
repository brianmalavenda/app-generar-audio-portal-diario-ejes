from dotenv import load_dotenv
import os
from flask import Flask, request, send_file # jsonify
from flask_cors import CORS  
from gcloud_SA_access import get_access_token_service_account, get_project_id_service_account, synthesize_speech
from utils import leer_docx_completo 

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost"])

load_dotenv()
## Este endpoint recibe el archivo a sintetizar a audio
@app.route('/api_proxy/sintetizar_audio', methods=['POST'])
def generar_audio_from_file():
    print(f"Esto es lo que recibi como archivo: {request.files}")

    file_storage = request.files['file']
    print(f"A ver si funca: {file_storage}")

    filename = file_storage.filename
    if filename == '':
        return 'No file selected', 400
    
    # try:
    #     # Para leer el contenido de un FileStorage, usa .read() directamente
    #     text_ssml = file_storage.read().decode('utf-8')
    #     print("Contenido SSML leído correctamente")
    #     # Aquí puedes continuar con el procesamiento a Google Text-to-Speech
    # except UnicodeDecodeError:
    #     # Si hay problemas con la codificación, intenta con otra
    #     file_storage.stream.seek(0)  # Regresar al inicio del stream
    #     text_ssml = file_storage.read().decode('latin-1')
    #     print("Contenido leído con codificación latin-1")
    # except Exception as e:
    #     print(f"Error leyendo archivo SSML: {e}")
    #     return f'Error processing file: {e}', 500

    # Leer documento word
    texto = leer_docx_completo(file_storage)
    if texto:
        print(f"Texto extraído ({len(texto)} caracteres):")
        print(texto)

    text_size = len(texto.encode('utf-8'))
    is_long_audio = text_size > 5000

    if is_long_audio:
        extension = ".wav"
    else:
        extension = ".ogg"

    # Usar la autenticación por service account
    token = get_access_token_service_account()
    project_id = get_project_id_service_account()
    
    print(f"Texto a grabar audio:\n{texto}")

    if not token or not project_id:
        return "Error de autenticación con Google Cloud", 500

    result = synthesize_speech(texto, token, project_id, filename.split('.')[0])
    
    if result and 'audioContent' in result:
        try:
            import base64
            audio_data = base64.b64decode(result['audioContent'])
            
            # Crear directorio si no existe
            # audio_dir = "test/audios/"
            audio_dir = "shared-files/audio/"
            os.makedirs(audio_dir, exist_ok=True)
            
            # Crear nombre de archivo para el audio
            audio_filename = f"{os.path.splitext(filename)[0]}{extension}"
            print(f"Este es el archivo de audio {audio_filename}")
            # audio_path = os.path.join("/app/shared-files/audios/", audio_filename)
            audio_path = os.path.join(audio_dir, audio_filename)

            # Guardar archivo de audio
            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_data)
            
            print(f"Audio guardado en: {audio_path}")
            
            # Devolver el archivo de audio para descargar
            return send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype=f"audio/{extension}")
            
        except Exception as e:
            print(f"Error procesando audio: {e}")
            return f"Error procesando audio: {e}", 500
    else:
        print("Error en la síntesis de voz")
        return "Error en la síntesis de voz", 500

## Este endpoint recibe un nombre de archivo por parametro ?filename=ssml_test_03.xml
@app.route('/api_proxy/generar_audio', methods=['POST'])
def generar_audio():
    filename = request.args.get('filename')
    if not filename:
        return "Filename es requerido", 400
    
    # Ruta corregida
    path_salida = "/app/shared-files/diario_ssml/"
    documento_salida = os.path.join(path_salida, filename)
    
    print(f"Estoy buscando el archivo {filename} en la carpeta {path_salida}")

    try:
        with open(documento_salida, "r", encoding="utf-8") as file:
            text_ssml = file.read()
            print("Contenido SSML leído correctamente")
    except Exception as e:
        print(f"Error leyendo archivo SSML: {e}")
        return f"Error leyendo archivo: {e}", 500

    # Leer documento word
    # texto = leer_docx_completo(file_storage)
    if text_ssml:
        print(f"Texto extraído ({len(text_ssml)} caracteres):")
        print(text_ssml)

    text_size = len(text_ssml.encode('utf-8'))
    is_long_audio = text_size > 5000

    if is_long_audio:
        extension = ".wav"
    else:
        extension = ".ogg"
    # Usar la autenticación por service account
    token = get_access_token_service_account()
    project_id = get_project_id_service_account()
    
    if not token or not project_id:
        return "Error de autenticación con Google Cloud", 500

    result = synthesize_speech(text_ssml, token, project_id)
    
    if result and 'audioContent' in result:
        try:
            import base64
            audio_data = base64.b64decode(result['audioContent'])
            
            # Crear directorio si no existe
            # audio_dir = "test/audios/"
            audio_dir = "shared-files/audio/"
            os.makedirs(audio_dir, exist_ok=True)
            
            # Crear nombre de archivo para el audio
            audio_filename = f"{os.path.splitext(filename)[0]}{extension}"
            print(f"Este es el archivo de audio {audio_filename}")
            # audio_path = os.path.join("/app/shared-files/audios/", audio_filename)
            audio_path = os.path.join(audio_dir, audio_filename)

            # Guardar archivo de audio
            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio_data)
            
            print(f"Audio guardado en: {audio_path}")
            
            # Devolver el archivo de audio para descargar
            return send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype=f"audio/{extension}")
            
        except Exception as e:
            print(f"Error procesando audio: {e}")
            return f"Error procesando audio: {e}", 500
    else:
        print("Error en la síntesis de voz")
        return "Error en la síntesis de voz", 500
    
@app.get("/api-proxy/health")
def health():
    return {"message": "Mandame un audio que te lo traduzco al toque"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)