from pydub import AudioSegment
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class OptimizeAudio:
    original: str = "0 MB"
    comprimido: str = "0 MB"
    ratio_compresion: str = "0 %"

def optimize_audio(input_wav_path, output_ogg_path=None):
    """
    Optimiza audio para WhatsApp y Telegram
    Args:
        input_wav_path (str): Ruta del archivo WAV
        output_ogg_path (str): Ruta de salida OGG (opcional)
    Returns:
        str: Ruta del archivo optimizado
    """
    
    if output_ogg_path is None:
        base_name = os.path.splitext(input_wav_path)[0]
        output_ogg_path = f"{base_name}.ogg"
    
    try:
        # Cargar audio WAV
        audio = AudioSegment.from_wav(input_wav_path)
        
        logger.info("backend - convert_audio.py - optimize_audio - 01 - Audio WAV cargado correctamente")
        # Aplicar optimizaciones para reducir tamaño
        # 1. Reducir sample rate si es muy alto
        if audio.frame_rate > 22050:
            audio = audio.set_frame_rate(22050)
        
        # 2. Convertir a mono (reduce tamaño a la mitad)
        audio = audio.set_channels(1)
        
        # 3. Comprimir con bitrate bajo para voz
        audio.export(
            output_ogg_path, 
            format='ogg', 
            bitrate='48k',  # Optimizado para voz
            parameters=["-ac", "1"]  # Fuerza canal mono
        )
        
        # Verificar tamaño del archivo
        original_size = os.path.getsize(input_wav_path)
        compressed_size = os.path.getsize(output_ogg_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"✅ Conversión exitosa!")
        # / 1024 / 1024 convierto bytes a kilobytes y luego a megabytes
        print(f"📁 Original: {original_size / 1024 / 1024:.1f} MB")
        print(f"📁 Comprimido: {compressed_size / 1024 / 1024:.1f} MB")
        print(f"📊 Compresión: {compression_ratio:.1f}%")
        
        audio_optimizado = OptimizeAudio(
            original = original_size,
            comprimido = compressed_size,
            ratio_compresion = compression_ratio
        )

        return audio_optimizado
        
    except Exception as e:
        print(f"❌ Error en la optimización: {e}")
        return None

# Ejemplo de uso
# input_file = "shared-files/audio/audio-descargo.wav"
# output_file = optimize_audio_for_messaging(input_file)