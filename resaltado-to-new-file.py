# -*- coding: utf-8 -*-
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
import os

def extraer_texto_resaltado(input_path, output_path):
    """
    Extrae texto resaltado en amarillo de un documento Word y lo guarda en un nuevo documento.
    Args:
        input_path (str): Ruta al documento Word de entrada (.docx)
        output_path (str): Ruta donde se guardará el nuevo documento con el texto extraído
    """
    try:
        # Cargar el documento
        doc = Document(input_path)
        
        # Crear un nuevo documento para el texto extraído
        nuevo_doc = Document()
        nuevo_doc.add_heading('Texto Resaltado en Amarillo', 0)
        
        # Bandera para verificar si encontramos texto resaltado
        texto_encontrado = False
        
        # Iterar a través de todos los párrafos del documento
        for paragraph in doc.paragraphs:
            texto_parrafo = ""
            
            # Iterar a través de todos los "runs" (fragmentos de texto con formato) en el párrafo
            for run in paragraph.runs:
                # Verificar si el texto está resaltado en amarillo
                if run.font.highlight_color == WD_COLOR_INDEX.YELLOW:
                    texto_parrafo += run.text
                    texto_encontrado = True
            
            # Si encontramos texto resaltado en este párrafo, añadirlo al nuevo documento
            if texto_parrafo:
                nuevo_doc.add_paragraph(texto_parrafo)
        
        # Guardar el nuevo documento si se encontró texto resaltado
        if texto_encontrado:
            nuevo_doc.save(output_path)
            print(f"¡Proceso completado! Texto extraído guardado en: {output_path}")
        else:
            print("No se encontró texto resaltado en amarillo en el documento.")
    
    except Exception as e:
        print(f"Error al procesar el documento: {str(e)}")

if __name__ == "__main__":
    # Configurar rutas de entrada y salida
    documento_entrada = "250908LN.docx"  # Cambia por la ruta de tu documento
    documento_salida = "texto_resaltado.docx"
    
    # Verificar si el archivo de entrada existe
    if not os.path.exists(documento_entrada):
        print(f"Error: El archivo {documento_entrada} no existe.")
    else:
        # Ejecutar la función principal
        extraer_texto_resaltado(documento_entrada, documento_salida)
