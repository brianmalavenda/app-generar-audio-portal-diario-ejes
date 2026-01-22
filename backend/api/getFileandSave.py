from flask import Flask, request
import os

app = Flask(__name__)
SAVE_FOLDER = os.getenv("SAVE_FOLDER")

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    # Guardar el archivo en la carpeta destino
    file_path = os.path.join(SAVE_FOLDER, file.filename)
    file.save(file_path)
    
    return 'File uploaded successfully', 200