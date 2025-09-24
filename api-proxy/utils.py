from docx import Document
import io

def leer_docx_completo(file_storage):
    """Lee un archivo DOCX incluyendo texto de tablas"""
    try:
        file_stream = io.BytesIO(file_storage.read())
        doc = Document(file_stream)
        
        texto_completo = []
        
        # Leer párrafos
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                texto_completo.append(paragraph.text)
        
        # Leer tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        texto_completo.append(cell.text)
        
        return '\n'.join(texto_completo)
        
    except Exception as e:
        print(f"Error leyendo DOCX: {e}")
        return None