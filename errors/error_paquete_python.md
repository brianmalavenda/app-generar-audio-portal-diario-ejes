# Error versionado paquete

api-proxy-container | api_proxy - generar_audio - Error: project_id es requerido
api-proxy-container | Traceback (most recent call last):
api-proxy-container |   File "/usr/local/lib/python3.11/site-packages/api_proxy/routes.py", line 42, in generar_audio
api-proxy-container |     gcloud_client = GoogleCloudTTSClient()
api-proxy-container |                     ^^^^^^^^^^^^^^^^^^^^^^
api-proxy-container |   File "/usr/local/lib/python3.11/site-packages/api_proxy/gcloud_tts/client.py", line 15, in __init__
api-proxy-container |     credentials = GoogleCloudCredentials()
api-proxy-container |                   ^^^^^^^^^^^^^^^^^^^^^^^^
api-proxy-container |   File "<string>", line 6, in __init__
api-proxy-container |   File "/usr/local/lib/python3.11/site-packages/api_proxy/gcloud_tts/auth/credentials.py", line 15, in __post_init__
api-proxy-container |     raise ValueError("project_id es requerido")
api-proxy-container | ValueError: project_id es requerido
api-proxy-container | 172.19.0.2 - - [06/Feb/2026 10:57:17] "POST /api_proxy/generar_audio HTTP/1.1" 500 -