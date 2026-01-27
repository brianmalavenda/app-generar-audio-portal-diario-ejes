# 001 - CONTENEDOR BACKEND NO PUEDE CONECTARSE CON API-PROXY

## Detalle

backend-container |            ^^^^^^^^^^^^^
backend-container |   File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 841, in urlopen
backend-container |     retries = retries.increment(
backend-container |               ^^^^^^^^^^^^^^^^^^
backend-container |   File "/usr/local/lib/python3.11/site-packages/urllib3/util/retry.py", line 535, in increment
backend-container |     raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
backend-container | urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='api-proxy', port=5000): Max retries exceeded with url: /api_proxy/generar_audio?filename=procesado_test-5.docx (Caused by ConnectTimeoutError(<HTTPConnection(host='api-proxy', port=5000) at 0x71113ac59ed0>, 'Connection to api-proxy timed out. (connect timeout=None)'))

## Diagnóstico

1) El contenedor api-proxy no escucha a otro contenedor en la configuración por defecto de localhost. Flask debe escuchar en 0.0.0.0 (todas las interfaces de red).
    app.run(host='0.0.0.0', port=5000)
2) Conflicto de puertos?
    Revise que en el docker-compose la configuracion de los puertos de los contenedores esten OK. En api-proxy expongo al host (izquierda) el puerto 5001 y en el contenedor, la app queda expuesta en el 5000 (derecha), lo mismo en el backend pero al host le expongo el 5000 y luego el contenedor expone su propia app tambien en el 5000.
3) El contenedor no puede conectarse con otro dentro de su propia red
    la red bridge configurada dentro del docker-compose se llama tss-network. Conectado dentro del contenedor de backend intente llegar al api-proxy a través de curl -f http://api-proxy:5000/api-proxy/health y no pude. Puede ser un problema de DNS dentro de la red, para descartarlo intente pegarle directamente a la IP curl -f http://172.19.0.4:5000/api-proxy/health y tampoco tuve exito.
4) Problemas de internet, el contenedor no puede conectarse a internet
    El problema parece ser más general, intente pegarle al DNS de google curl -f 8.8.8.8 y tampoco pude por lo tanto el problema esta en que cada contenedor quedó completamente aislado.    
5) Bloqueo de firewall?
    ufw status //esta desactivado
    Si tuviesemos ufw activado podría ser que este bloqueando el flujo de transacciones dentro de bridge porque son forwardings y por defecto ufw las bloquea
6) Aunque WSL tenga internet, Docker necesita permiso para "pasar" paquetes de una interfaz a otra. Verifica esto:
    sysctl net.ipv4.conf.all.forwarding
    Si devuelve 0, actívalo con: sudo sysctl -w net.ipv4.conf.all.forwarding=1.
7) Docker inserta reglas en el firewall interno de Linux (iptables) para permitir el tráfico. Si ayer funcionaba y hoy no, tras el deploy las reglas pudieron quedar huérfanas. Esto pudo haber pasado por un apagón abrupto de la computadora con la virtualización de linux corriendo y los contenedores levantados
    sudo iptables -t nat -F
    sudo iptables -t filter -F

## Solución

docker-compose down
docker network prune -f

sudo iptables -t nat -F
sudo iptables -t filter -F

apt-get update && apg-get upgrade -y

sudo systemctl restart docker

