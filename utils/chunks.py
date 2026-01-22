# Dividir textos muy largos en chunks. De esta manera casi que se vuelve imperativo la utilización de colas como RabbitMQ o similares 
# para que no se pierda ninguna petición que sería un fragmento de un audio largo. En este caso, que una petición falle pone en riesgo todo el audio.

# Aca por ejemplo max_caracteres hace referencia a el limite para la API de sintetizador de voz de Google corta = 5,000 caracteres por request
def dividir_texto_largo(texto, max_caracteres=100000):
    """Divide texto en chunks manejables"""
    chunks = []
    
    # Dividir por párrafos si es posible
    parrafos = texto.split('\n\n')
    
    chunk_actual = ""
    for parrafo in parrafos:
        if len(chunk_actual) + len(parrafo) <= max_caracteres:
            chunk_actual += parrafo + "\n\n"
        else:
            if chunk_actual:
                chunks.append(chunk_actual.strip())
            chunk_actual = parrafo + "\n\n"
    
    if chunk_actual:
        chunks.append(chunk_actual.strip())
    
    # Esto devuelve una colección de chunks para luego recorrerlos iterando y sintetetizando cada uno
    return chunks


    from google.cloud import texttospeech

def sintesis_corta(texto, archivo_salida):
    """Para textos cortos (hasta 5000 caracteres) - Respuesta inmediata"""
    # Acá se usa la librería de google, podríamos directamente pegarle a la API
    client = texttospeech.TextToSpeechClient()
    texto_total = []
    texto_total = dividir_texto_largo(texto, max_caracteres=5000)
    
    for texto in texto_total:
        synthesis_input = texttospeech.SynthesisInput(text=texto)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-ES",
            name="es-ES-Standard-A"
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        try:
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Aca guardamos cada audio por separado. Esto debería tener un identificador de orden para luego unirlos en un solo audio
            with open(archivo_salida, "wb") as out:
                out.write(response.audio_content)
            
            return True, "Audio generado exitosamente"
            
        except Exception as e:
            return False, f"Error: {str(e)}"