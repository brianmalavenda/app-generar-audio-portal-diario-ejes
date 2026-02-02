
def validar_procesar(documento_salida):
    """Procesa archivo detectando automáticamente su tipo"""
    
    print(f"Procesando archivo: {documento_salida}")
    
    
    # Determinar si es SSML (XML) o texto plano
    is_ssml = file_ext in ['.xml', '.ssml']
    
    # Validar SSML si corresponde
    if is_ssml:
        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            raise HTTPException(400, f"XML inválido: {str(e)}")


    # Verificar extensión
    _, ext = os.path.splitext(documento_salida.lower())
    
    try:
        if ext == '.docx':
            # Procesar como DOCX
            return procesar_docx(documento_salida)
            
        elif ext == '.xml':
            # Procesar como XML
            return procesar_xml(documento_salida)

        elif ext == '.pdf':
            # Procesar como PDF
            return procesar_pdf(documento_salida)

        elif ext == '.txt':
            # Procesar como TXT
            return procesar_texto(documento_salida)
            
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        return None