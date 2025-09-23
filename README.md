# INCICAR ENTORNO VIRTUAL DE PYTHON
python3 -m venv ~/entorno_python
source ~/entorno_python/bin/activate

## Instalar dependencias
```
    pip install python-docx
    pip install request
    pip install google-cloud-texttospeech
```
o
```
    pip install -r requirements.txt 
```

**Preparar el documento:**
Asegúrate de que tu documento esté en formato .docx (no .doc)
Resalta con amarillo el texto que quieres conservar

**Configurar las rutas:**
Modifica la variable documento_entrada con la ruta a tu documento
El script guardará el resultado en texto_resaltado.docx (puedes cambiar este nombre)

**Ejecutar el script:**
```
python nombre_del_script.py
```

### ⚠️ Limitaciones y consideraciones:
Solo funciona con archivos .docx (no con los antiguos .doc)
Detecta específicamente el color amarillo de resaltado (WD_COLOR_INDEX.YELLOW)
El texto extraído mantendrá su estructura original en párrafos
Si no encuentra texto resaltado en amarillo, te lo indicará
🔧 Posibles mejoras:
Si necesitas detectar otros colores o formatos adicionales (como subrayado), puedo ayudarte a modificar el script. También puedo ayudarte a crea*r una interfaz gráfica sencilla si prefieres no trabajar con la línea de comandos.


## Iniciarlizar nuestro cliente de Google cloud

Una vez inicializada la conexion y autenticacion con gcloud podremos ejecutar el script sin problemas y nos generará de salida un archivo de audio con el nombre que le indicamos en el script.

```
    gcloud init --console-only
```

## Generar un texto de formato SSML**

## API

    headers = {
        "Authorization": f"Bearer {token}",
        "x-goog-user-project": project_id,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "input": {
            "ssml": text
        },
        "voice": {
            "languageCode": "es-US", # Esto indica el idioma español
            # "name": "es-US-Standard-A", # Esto indica la voz específica
            # "ssmlGender": "FEMALE" # Género de la voz
        },
        "audioConfig": {
            "audioEncoding": "MP3"
        }
    }

## Para utilizar el texto directamente en el script

    # TEXT = """<speak>
    #     <voice name="es-US-Standard-B" gender="MALE">
    #         <prosody rate="medium" volume="loud">
    #         <emphasis level="strong">250908LN Protestas masivas en Europa contra Israel: 900 detenidos en Londres</emphasis>
    #         </prosody>
    #     </voice>
        
    #     <break time="2s"/>
        
    #     <voice name="es-US-Standard-A" gender="FEMALE">
    #         <prosody rate="fast" volume="medium">
    #         La policía metropolitana de Londres (MET) indicó que 857 personas fueron detenidas en cumplimiento de la ley antiterrorista, después de una protesta organizada el sábado en apoyo de una organización proscrita. Además, otras 33 personas fueron detenidas acusadas de atacar a agentes de policía y por otros delitos contra el orden público.
    #         </prosody>
    #     </voice>
    #     </speak>"""
    # se utilizan 3 comillas dobles para permitir saltos de línea y comillas simples dentro del texto


# PASOS

1. Importar el archivo de texto con subrayado amarillo
2. Procesar y generar archivo de texto plano que tenga por contenido solo lo subrayado del archivo fuente
3. Procesarlo a SSML format para generar de esta manera una "forma" de lectura
4. Sintetizamos el archivo SSML y lo exportamos en un audio en formato ogg 
5. Para casos donde el archivo sea pesado, ver si esto es por cantidad de caracteres o tamaño del archivo, generar varios procesos a la vez de traducción de audio. Para esto hay que:
   
   1. dividir el archivo en formato SSML en sub-archivos
   2. levantar contenedores de docker por cada sub-proceso de sintetizacion en gcloud con text-to-speech asi se procesan en paralelo
   3. tengo que tener un script en paralelo corriendo para que cuando terminen de procesar el archivo en todas sus secciones y se guarden en una carpeta, el proceso anterior envie un aviso a esta API que se encargue de "unir" todo el audio en un solo audio para exportar (formato .ogg )


Notas: 
   1. El título tiene que poder tomarse del archivo subrayado aunque este sin subrayar
   2. El código del principio no es necesario que esté o hay que omitirlo de la lectura



## 250912

### ver
1. El diario procesado debe poder tomar los títulos de las notas en formato Haeding 1 y ponerlos al principio de la nota
2. Si no tiene título en formato Heading 1 debe indicar un error en el momento de procesar el archivo indicando que el formato del diario no es el correcto. "Los títulos de cada nota deben comenzar por un título que tenga formato Heading 1"

### hicimos
1. Generamos una lista de objetos nota que nos ayudo a estructurar las propiedades de cada nota que componen el bodoque
2. Distinguimos cada título en formato Heading 1 para diferenciar una nota de otra y poder tener una definicion clara de comienzo y fin de cada una
3. Guardamos el contenido en el archivo iterando por la lista y nos aseguramos que se respeto el formato de titulo Heading 1 y el cuerpo de la nota que sea solo del texto resaltado

## 250915

### hicimos
1. El título en formato Heading 1 en el archivo de resultado se repite en la primer oracion del cuerpo de la nota, revisar para que no pase
2. Post procesamiento y resultado final hay que reprocesarlo para convertirlo en formato SSML.
   1. Encabezadao: <?xml version="1.0"?>
        <speak>
   2. Título: <voice name="es-US-Standard-B" gender="MALE">
        <prosody rate="medium" volume="loud">
        <emphasis level="strong">
   3. Cuerpo: <voice name="es-US-Standard-A" gender="FEMALE">
        <prosody rate="medium" volume="medium">
   4. Cierre final: <speak>
3. ver cantidad de caracteres resultante, cantidad de palabras, tiempo que tarda en procesar el archivo y re-evaluar viabilidad del proyecto
4. Hay que crear una estructura de carpetas que sea coincidente con la arquitectura de la app. 
   1. api
   2. back
   3. front
5. Una vez que queda separada la api-gateway del back y del front, considero esta parte como otra app. Esto implica que tiene su propias variables de entorno, dependencias, file system, etc. Esto se traducirá en un contenedor docker que simulará otro servidor. Para eso primero creamos un dockerfile para crear la imagen de la app. Luego con un archivo docker-compose.yml podemos orquestar los contenedores y dejarlo listo para que al levantarlo podamos desde afuera acceder a la API desde http://localhost:8000


## EJECUTAR CONTENEDORES

sudo docker build -t backend-python-images .
sudo docker build -t frontend-images .

<!-- creamos la red bridge para comunicarse entre contenedores -->
docker network create tts-network

docker run -it -p 5000:5000 -v $(pwd)/shared-data:app/shared-files --name backend-container-api  --network tts-network backend-python-images

docker run -it -p 3000:3000 --name frontend-container --network tts-network frontend-images

<!-- entrar dentro de mi contenedor -->
docker exec -it backend-container-api /bin/bash
<!-- buscar un archivo -->
docker exec nombre_de_tu_contenedor find / -name "*.txt" 2>/dev/null

docker volumen ls


docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker rmi $(docker images -q) 
&& rmdir shared-data


docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker build -t api-proxy:latest ./api-proxy

# En tu servidor, en la carpeta del proyecto
### deploy.sh

docker swarm init
docker secret create google_credentials cred/google-credentials.json
docker stack deploy -c docker-compose.yml tu-app

# En tu servidor, una sola vez:
cd ~/Repositorio/app-generar-audio-portal-diario-ejes
docker swarm init
docker secret create google_credentials api/cred/google-credentials.json
docker stack deploy -c docker-compose.yml audio-app