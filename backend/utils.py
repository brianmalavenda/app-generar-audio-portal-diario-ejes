from pydub import AudioSegment

def convert_wav_to_ogg(input_wav, output_ogg, bitrate='192k'):
    """
    Convierte WAV a OGG usando pydub
    """
    try:
        # Cargar archivo WAV
        audio = AudioSegment.mp3(input_mp3
        
        # Exportar como OGG
        audio.export(
            output_ogg, 
            format='ogg',
            codec='libvorbis',
            bitrate=bitrate
        )
        
        print(f"✅ Convertido: {input_mp3} → {output_ogg}")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False