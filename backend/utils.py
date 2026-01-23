from pydub import AudioSegment

def convert_wav_to_ogg(input_wav, output_ogg, bitrate='192k'):
    """
    Convierte WAV a OGG usando pydub
    """
    try:
        # Cargar archivo WAV
        audio = AudioSegment.from_wav(input_wav)
        
        # Exportar como OGG
        audio.export(
            output_ogg, 
            format='ogg',
            codec='libvorbis',
            bitrate=bitrate
        )
        
        print(f"✅ Convertido: {input_wav} → {output_ogg}")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False


def convert_wav_to_mp3_pydub(input_wav, output_mp3, bitrate='192k'):
    """
    Conversión más simple y directa
    Calidad: Excelente
    Instalación: Fácil
    """
    audio = AudioSegment.from_wav(input_wav)
    audio.export(
        output_mp3,
        format='mp3',
        bitrate=bitrate
    )
    return True