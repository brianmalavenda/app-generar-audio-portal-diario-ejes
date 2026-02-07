# DESCRIPCION ERROR 

 2 warnings found (use docker --debug to expand):
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "GOOGLE_APPLICATION_CREDENTIALS") (line 32)
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "GOOGLE_APPLICATION_CREDENTIALS") (line 33)
root@brian:/home/brian/Repositorio/app-generar-audio-portal-diario-ejes/api_proxy# docker run -d --name api-proxy-container -p 5001:5000 --entrypoint python api_proxy:1.0.7
4b5855495604a784cf29c4c6bce87c7e399bddfadfc027a959a137ffd897c926
root@brian:/home/brian/Repositorio/app-generar-audio-portal-diario-ejes/api_proxy# docker ps -a
CONTAINER ID   IMAGE             COMMAND    CREATED         STATUS                     PORTS     NAMES
4b5855495604   api_proxy:1.0.7   "python"   6 seconds ago   Exited (0) 3 seconds ago             api-proxy-container

creo la imagen pero fallo al crear el contenedor. Con docker logs no logro que el contenedor me muestre ningun error. Me ayudas a encontrar que puede estar funcionando mal paraque no levante el contenedor?

# SOLUCION

El contenedor se crea pero exite inmediatamente (Exited (0)). El problema es que ejecutaste python sin argumentos, así que abre el intérprete y cierra al no tener TTY.

docker run -d \
  --name api-proxy-container \
  -p 5001:5000 \
  --entrypoint python \
  api_proxy:1.0.7 \
  -m api_proxy