from google.cloud import storage
from datetime import datetime, timedelta

def generate_signed_url(bucket_name, blob_name, expiration_minutes=60):
    """Genera URL firmada temporal para el archivo"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        method='GET'
    )
    return url

@app.route('/api/get_audio_url', methods=['GET'])
def get_audio_url():
    filename = request.args.get('filename')
    # Generar URL firmada
    audio_url = generate_signed_url('tu-bucket-audio', f"audios/{filename}.wav")
    
    return jsonify({
        "audio_url": audio_url,
        "expires_in": "60 minutes"
    })