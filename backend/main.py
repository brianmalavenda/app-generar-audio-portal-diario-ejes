# -*- coding: utf-8 -*-
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import os
import xml.dom.minidom
from flask import Flask, request, jsonify, send_file
import requests
from flask_cors import CORS  # Importa la extensión CORS
import os

app = Flask(__name__)
# Usar ruta absoluta con valor por defecto
SAVE_FOLDER = os.getenv('SAVE_FOLDER', '/app/shared-files/diario_pintado/')
# Configura CORS para permitir solicitudes desde localhost:3000
CORS(app, origins=["http://localhost:3000"])
os.makedirs(SAVE_FOLDER, exist_ok=True)
print(f"Directorio de guardado: {SAVE_FOLDER}")

class Heading1NotFoundException(Exception):
    """Excepción personalizada para cuando no se encuentra un Heading 1"""
    pass

@app.route('/api/archivos_procesados')
def listar_archivos_procesados():
    import glob
    archivos = glob.glob("/app/shared-files/diario_procesado/*.docx")
    archivos_lista = [os.path.basename(archivo) for archivo in archivos]
    
    return jsonify({
        'directorio': os.path.abspath("/app/shared-files/diario_procesado/"),
        'archivos': archivos_lista,
        'total': len(archivos_lista)
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    # Asegurarse de que el directorio existe (por si acaso)
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    file_path = os.path.join(SAVE_FOLDER, file.filename)
    print(f"Guardando archivo en: {file_path}")
    file.save(file_path)
    print(f"El archivo se llama: {file.filename}")

    filename_sin_extension = file.filename.split('.')
    
    nombre_archivo_procesado = "procesado_" + filename_sin_extension[0] + ".docx"
    print(f"Nombre de mi archivo procesado {nombre_archivo_procesado}")
    documento_salida = os.path.join('/app/shared-files/diario_procesado/', nombre_archivo_procesado)
 
    nombre_archivo_ssml = "ssml_" + filename_sin_extension[0] + ".xml"
    print(f"Nombre de mi archivo ssml {nombre_archivo_ssml}")
    xml_salida = os.path.join('/app/shared-files/diario_ssml/', nombre_archivo_ssml)
    
    extraer_texto_resaltado(file_path, documento_salida)
    print("Procese el documento y extraje lo resaltado, vamos bien")
    palabras_caracteres = convertir_a_formato_ssml(documento_salida, xml_salida)
    tamanio_megabytes_archivo = tamanio_archivo_en_megabytes(xml_salida)
    print ({"status": "OK", "Cantidad de palabras en SSML:": palabras_caracteres[0], "Cantidad de caracteres en SSML": palabras_caracteres[1], "Tamaño del archivo SSML en megabytes" : tamanio_megabytes_archivo })
    
    return jsonify({"palabras:": palabras_caracteres[0], "caracteres": palabras_caracteres[1], "tamanio" : tamanio_megabytes_archivo }), 200

# @app.route('/api/descargar_doc_procesado', methods=['GET'])
# def descargar_doc_procesado():
#     filename = request.args.get('filename')
#     new_filename = 'procesado_'+filename
#     file_path = os.path.join('/app/shared-files/diario_procesado', new_filename)
#     if not os.path.isfile(file_path):
#         return 'No existe el archivo que estas buscando', 404
#     return send_file(file_path, as_attachment=True)

@app.route('/api/descargar_doc_procesado', methods=['POST'])
def descargar_doc_procesado():
    filename = request.json.get('filename')  # Ahora viene en el body
    
    if not filename:
        return jsonify({'error': 'Filename parameter is required'}), 400
    
    # Sanitizar el filename para seguridad
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Invalid filename'}), 400
    
    file_path = os.path.join("procesados/", filename)
    
    print(f"Buscando archivo en: {file_path}")  # Debug
    print(f"Archivo existe: {os.path.exists(file_path)}")  # Debug

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Verificar que es un archivo y no un directorio
        if not os.path.isfile(file_path):
            return jsonify({'error': 'Path is not a file'}), 400
            
        # Debug: información del archivo
        file_stats = os.stat(file_path)
        print(f"Tamaño del archivo: {file_stats.st_size} bytes")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            conditional=True  # Esto permite el 304 para cache, pero fuerza descarga si es necesario
        )
    except Exception as e:
        print(f"Error al enviar archivo: {e}")
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

def extraer_texto_resaltado(input_path, output_path):
    """
    Extrae texto resaltado en amarillo de un documento Word y lo guarda en un nuevo documento.
    Args:
        input_path (str): Ruta al documento Word de entrada (.docx)
        output_dir (str): Directorio donde se guardará el nuevo documento con el texto extraído
    """
    try:
        # Cargar el documento
        doc = Document(input_path)        
        nuevo_doc = Document()
        contador_notas = 0
        nota = []
        
        for paragraph in doc.paragraphs:
            # Iterar a través de todos los "runs" (fragmentos de texto con formato) en el párrafo
            # busca titulos de notas  
            if paragraph.style.name.startswith('Heading 1'):
                if len(nota) == 0:
                    #creo la primera nota
                    nota.append({
                        "id": contador_notas,
                        "titulo": paragraph.text,
                        "cuerpo": [],
                        "estado": "pendiente" # la nota cambiara de estado a completa cuando se acabe el documento o cuando se encuentre otro heading 1
                    })
                else:
                    # Si encontramos otro Heading 1, validamos que la nota tenga cuerpo antes de iniciar una nueva
                    if len(nota[contador_notas]["cuerpo"]) > 0:
                        nota[contador_notas]["estado"] = "completa"
                        # print(f"Nota completa: {nota}")
                        contador_notas += 1
                        # Iniciar una nueva nota
                        nota.append({
                            "id": contador_notas,
                            "titulo": paragraph.text,
                            "cuerpo": [],
                            "estado": "pendiente"
                        })
            for run in paragraph.runs:                              
                # Verificar si el texto está resaltado en amarillo
                if run.font.highlight_color == WD_COLOR_INDEX.YELLOW:
                    if not paragraph.style.name.startswith('Heading 1'):
                        texto_resaltado = run.text
                        # Añadir el párrafo con su índice
                        nota[contador_notas]['cuerpo'].append({
                            'indice': len(nota[contador_notas]['cuerpo']) + 1,
                            'texto': texto_resaltado
                        })                                          
        
        # Guardar las notas en el nuevo documento
        for nota_a_guardar in nota:
            nuevo_doc.add_heading(nota_a_guardar["titulo"], level=1)
            for parrafo in nota_a_guardar["cuerpo"]:
                nuevo_doc.add_paragraph(f"{parrafo['texto']}")                
        
        # Guardar el documento
        nuevo_doc.save(output_path)

        print(f"¡Proceso completado! Texto extraído guardado en: {output_path}")
        return output_path  # Devolver la ruta del archivo guardado
        
    except Heading1NotFoundException as e:
        print(f"Error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error al procesar el documento: {str(e)}")
        raise

def contar_cantidad_de_palabras(texto):
    """
    Cuenta la cantidad de palabras en un texto dado.
    Args:
        texto (str): El texto en el que se contarán las palabras.
    Returns:
        int: La cantidad de palabras en el texto.
    """
    texto = texto.replace(',', '') # eliminar comas para un conteo más preciso
    texto = texto.replace('.', '') # eliminar puntos para un conteo más preciso
    palabras = texto.split()
    return len(palabras)

def contar_cantidad_de_caracteres(texto):
    """
    Cuenta la cantidad de caracteres en un texto dado.
    Args:
        texto (str): El texto en el que se contarán los caracteres.
    Returns:
        int: La cantidad de caracteres en el texto.
    """
    return len(texto)

def tamanio_archivo_en_megabytes(ruta_archivo):
    """
    Obtiene el tamaño de un archivo en megabytes.
    Args:
        ruta_archivo (str): La ruta al archivo.
    Returns:
        float: El tamaño del archivo en megabytes.
    """
    if os.path.isfile(ruta_archivo):
        tamaño_bytes = os.path.getsize(ruta_archivo)
        tamaño_megabytes = tamaño_bytes / (1024 * 1024)  # Convertir bytes a megabytes
        return tamaño_megabytes
    else:
        raise FileNotFoundError(f"El archivo XML no existe.")

def convertir_a_formato_ssml(input_path,output_path):
    """
    Convierte el texto del documento de salida a formato SSML.
    Args:
        documento_salida (str): Ruta al documento Word de salida (.docx)
    """
    try:
        doc = Document(input_path)
        ssml_output_string = '<?xml version="1.0"?><speak>'
        
        """
        Encabezado: 
            <?xml version="1.0"?>
            <speak>
        Heading 1 formato SSML:
            <voice name="es-US-Standard-B" gender="MALE">
            <prosody rate="medium" volume="loud">
            <emphasis level="strong">

        Cuerpo formato SSML:
            <voice name="es-US-Standard-A" gender="FEMALE">
            <prosody rate="medium" volume="medium">
        """
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading 1'):
                ssml_output_string += f'<voice name="es-US-Standard-B" gender="MALE"><prosody rate="medium" volume="loud"><emphasis level="strong">{paragraph.text}</emphasis></prosody></voice>\n'
            else:
                ssml_output_string += f'<voice name="es-US-Standard-A" gender="FEMALE"><prosody rate="medium" volume="medium">{paragraph.text}</prosody></voice>'

        ssml_output_string += '</speak>'
    
        # Parse the XML string with minidom
        dom = xml.dom.minidom.parseString(ssml_output_string)
        # ssml_output = dom.toxml()
        # If you want to pretty-print the XML
        ssml_output_pretty_xml = dom.toprettyxml(indent="    ")

        cantidad_palabras = contar_cantidad_de_palabras(ssml_output_pretty_xml)
        cantidad_caracteres = contar_cantidad_de_caracteres(ssml_output_pretty_xml)        
        
        # Guardar el SSML en un archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ssml_output_pretty_xml)
            
        print(f"¡SSML generado y guardado en: {output_path}!")
        return [cantidad_palabras, cantidad_caracteres]
    except Exception as e:
        print(f"Error al convertir a SSML: {str(e)}")
    # Obtener el nombre del archivo del cuerpo de la solicitud
    base_url = "http://localhost:5001/"
    url = base_url + filename
    # filename = request.get_json()['filename']
    file_path = os.path.join(SAVE_FOLDER, filename)

    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    response = requests.post(url)

    # return jsonify({'message': 'Audio generated successfully', 'filename': filename}), 200
    return send_file(file_path, as_attachment=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API funcionando"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# if __name__ == "__main__":
#     # Configurar rutas de entrada y salida
#     # este documento lo ingresa el usuario y el documento de salida tendra el mismo nombre pero con _resaltado
#     path_entrada = "/home/brian/Repositorio/app-generar-audio-portal-diario-ejes/diario_pintado/"
#     documento_entrada = path_entrada + "test" + ".docx"  # Cambia por la ruta de tu documento
#     path_salida = "/home/brian/Repositorio/app-generar-audio-portal-diario-ejes/diario_procesado/"
#     documento_salida = path_salida + "test" + "resaltado" + ".docx"
#     path_salida = "/home/brian/Repositorio/app-generar-audio-portal-diario-ejes/diario_ssml/"
#     xml_salida = path_salida + "test" + "formato_ssml" + ".xml"
    

#     # Verificar si el archivo de entrada existe
#     if not os.path.exists(documento_entrada):
#         print(f"Error: El archivo {documento_entrada} no existe.")
#     else:
#         # Ejecutar la función principal
#         extraer_texto_resaltado(documento_entrada, documento_salida)
#         palabras_caracteres = convertir_a_formato_ssml(documento_salida, xml_salida)
#         tamanio_megabytes_archivo = tamanio_archivo_en_megabytes(xml_salida)

#         print(f"Cantidad de palabras en SSML: {palabras_caracteres[0]}")
#         print(f"Cantidad de caracteres en SSML: {palabras_caracteres[1]}")
#         print(f"Tamaño del archivo SSML en megabytes: {tamanio_megabytes_archivo}")

