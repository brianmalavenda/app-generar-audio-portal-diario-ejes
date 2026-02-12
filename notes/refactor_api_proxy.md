# Sobrescribir entrypoint para ejecutar pip directamente
docker build --no-cache -t api_proxy:4.0.0 -t api_proxy:latest .
 
docker run --rm --entrypoint pip api_proxy:latest show api-proxy

docker run --rm --entrypoint cat api_proxy:1.1.0 /app/api_proxy/gcloud_tts/auth/credentials.py | grep -A5 "__post_init__"

docker run -d --name api-proxy-container -p 5001:5000 --entrypoint python api_proxy:3.0.0 -m api_proxy

docker run -d   --name api-proxy-container   -p 5001:5000   --entrypoint python   api_proxy:1.0.1   -m api_proxy

