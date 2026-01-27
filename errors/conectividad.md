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
2) Problemas de internet, el contenedor no puede conectarse a internet
3) El contenedor no puede resolver las direcciones IP, problemas con el DNS
4) Problema con las redes virtuales de docker. Para eso hay que reiniciar el servicio de docker
    sudo systemctl restart docker
5) Conflicto de puertos?

## Solución



