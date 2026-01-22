import time
from google.api_core.operation import Operation
from google.cloud import texttospeech

def monitorear_operacion_larga(operation_name, timeout_minutes=30):
    """
    Monitorea una operación de síntesis larga hasta que termine
    
    Args:
        operation_name: El nombre de la operación (el 'name' de la respuesta)
        timeout_minutes: Tiempo máximo de espera en minutos
    
    Returns:
        dict: Resultado de la operación o error
    """
    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
    operation = client.transport.operations_client.get_operation(operation_name)
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    print(f"🔍 Monitoreando operación: {operation_name}")
    
    while not operation.done:
        # Verificar timeout
        if time.time() - start_time > timeout_seconds:
            return {
                "status": "timeout",
                "error": f"La operación excedió el tiempo límite de {timeout_minutes} minutos"
            }
        
        # Esperar antes de consultar nuevamente
        time.sleep(10)
        
        # Actualizar estado de la operación
        operation = client.transport.operations_client.get_operation(operation_name)
        
        # Mostrar progreso si está disponible
        if operation.metadata and 'progressPercentage' in str(operation.metadata):
            # Extraer porcentaje de progreso del metadata
            print(f"📊 Progreso: {operation.metadata.progress_percentage}%")
        else:
            print("⏳ Esperando que comience el procesamiento...")
    
    # La operación terminó
    if operation.error:
        return {
            "status": "error",
            "error": operation.error.message,
            "details": operation.error.details
        }
    else:
        return {
            "status": "success",
            "response": operation.response,
            "metadata": operation.metadata
        } 