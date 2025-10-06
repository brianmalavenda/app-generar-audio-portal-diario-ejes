"use client";
import React, { useState, useCallback } from "react";

interface FileStats {
  palabras: number;
  caracteres: number;
  tamanio: string;
}

interface AudioState {
  isGenerating: boolean;
  audioUrl: string | null;
  audioName: string | null;
  error: string | null;
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [fileStats, setFileStats] = useState<FileStats | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [audioState, setAudioState] = useState<AudioState>({
    isGenerating: false,
    audioUrl: null,
    audioName: null,
    error: null
  });

  // Función para formatear el tamaño del archivo a 2 decimales
  const formatFileSize = (sizeInMB: string) => {
    return parseFloat(sizeInMB).toFixed(2);
  };

  /**
   * 
   * @param file 
   * @description Subir el archivo al backend
   * @returns 
   */
  const uploadFileToBackend = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) { 
        const data: FileStats = await response.json();
        setFileStats(data);
        // Resetear estado de audio cuando se sube nuevo archivo
        setAudioState({
          isGenerating: false,
          audioUrl: null,
          audioName: null,
          error: null
        });
        return true;
      } else {
        const errorText = await response.text();
        setUploadMessage(`Error: ${errorText}`);
        return false;
      }
    } catch (error) {
      setUploadMessage(`Error de red: ${error}`);
      return false;
    }
  };

  const handleFileChange = async (selectedFile: File) => {
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setFileStats(null);
    setUploadMessage("");
    setIsUploading(true);

    // Subir el archivo inmediatamente al backend
    await uploadFileToBackend(selectedFile);
    
    setIsUploading(false);
  };

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  /**
   * @param dropFile
   * @description Cargar archivo desde area de drop input
   * @returns
   */
  const handleDrop = useCallback((dropFile: React.DragEvent<HTMLDivElement>) => {
    dropFile.preventDefault();
    setIsDragging(false);
    
    if (dropFile.dataTransfer.files && dropFile.dataTransfer.files[0]) {
      const selectedFile = dropFile.dataTransfer.files[0];
      if (selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.doc') || selectedFile.type === 'text/plain') {
        handleFileChange(selectedFile);
      } else {
        alert('Por favor, seleccione un archivo Word (.doc, .docx) o texto (.txt)');
      }
    }
  }, [handleFileChange]);

  /**
   * @param inputFile
   * @description Cargar archivo desde input
   */
  const handleFileInput = useCallback((inputFile: React.ChangeEvent<HTMLInputElement>) => {
    if (inputFile.target.files && inputFile.target.files[0]) {
      const selectedFile = inputFile.target.files[0];
      if (selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.doc') || selectedFile.type === 'text/plain') {
        handleFileChange(selectedFile);
      } else {
        alert('Por favor, seleccione un archivo Word (.doc, .docx) o texto (.txt)');
      }
    }
  }, [handleFileChange]);

  const handleExportToAudio = useCallback(async (filename: string) => {
    try {
      setAudioState({
        isGenerating: true,
        audioUrl: null,
        audioName: null,
        error: null
      });

      const response = await fetch(
        `http://localhost:5000/api/generar_audio?filename=procesado_${filename}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          mode: 'cors'
        }
      );

      if (response.ok) {            
        const data = await response.json();
        
        if (data.status === "OK") {
          // Construir la URL del audio
          const audioName = `procesado_${filename.split('.').slice(0, -1).join('.')}`;
          // generar un enlace al recurso que se encuentra en el backend en la carpeta app/shared-files/audio
          // const audioUrl = `http://localhost:5000/shared-files/audio/${audioName}.wav`;
          const audioUrl = data.public_audio_url;
          // const audioUrl = `http://localhost:5000/audio/${data.audio_file}`;
          console.log(audioUrl)

          setAudioState({
            isGenerating: false,
            audioUrl: audioUrl,
            audioName: audioName,
            error: null
          });
        } else {
          throw new Error(data.message || 'Error generando audio');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || `Error ${response.status}`);
      }
    } catch (error) {
      console.error('Error en la solicitud:', error);
      setAudioState({
        isGenerating: false,
        audioUrl: null,
        audioName: null,
        error: error instanceof Error ? error.message : 'Error desconocido'
      });
    }
  }, []);

  const handleDownloadAudio = useCallback(() => {
    if (audioState.audioUrl && audioState.audioName) {
      const a = document.createElement('a');
      a.href = audioState.audioUrl;
      a.download = audioState.audioUrl; //`${audioState.audioName}.wav`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  }, [audioState.audioUrl, audioState.audioName]);

  const handleDownloadText = async (filename: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/descargar_doc_procesado', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: filename
        })
      });
      
      const body_response = await response.json();

      if (body_response.status) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Error al descargar el archivo');
        alert('Error al descargar el archivo');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error al descargar el archivo');
    }
  };

  const AudioPlayer = () => {
    if (!audioState.audioUrl) return null;

    return (
      <div className="mt-6 p-4 bg-white rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Audio Generado</h3>
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <audio controls className="flex-1">
            <source src={audioState.audioUrl} type="audio/wav" />
            Tu navegador no soporta el elemento de audio.
          </audio>
          <button
            onClick={handleDownloadAudio}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition duration-300 flex items-center justify-center whitespace-nowrap"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Descargar audio
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Portal de envio de diarios</h1>
          <p className="text-lg text-gray-600">Carga tu archivo Word pintado, se procesará para extraer lo subrayado y se generará un audio listo para compartir por telegram o descargar</p>
        </div>

        <div 
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 mx-4 ${
            isDragging 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-blue-25'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!file ? (
            <>
              <div className="mb-6">
                <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Arrastra tu archivo Word aquí</h3>
              <label className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg cursor-pointer transition duration-300 inline-block">
                Seleccionar archivo
                <input 
                  type="file" 
                  accept=".doc,.docx,.txt" 
                  onChange={handleFileInput}
                  className="hidden"
                />
              </label>
              <p className="text-sm text-gray-500 mt-4">Formatos soportados: .doc, .docx, .txt</p>
            </>
          ) : (
            <div className="space-y-6">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
                  <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-800">{file.name}</h3>
                
                {isUploading && (
                  <div className="mt-4">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      <span className="ml-2 text-gray-600">Subiendo archivo...</span>
                    </div>
                  </div>
                )}
                
                {uploadMessage && (
                  <div className={`mt-4 p-3 rounded-lg ${uploadMessage.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {uploadMessage}
                  </div>
                )}
                
                {fileStats && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 w-full max-w-md">
                    <div className="bg-white rounded-lg p-4 shadow-sm border flex flex-col items-center justify-center">
                      <p className="text-sm text-gray-500">Tamaño</p>
                      <p className="text-lg font-semibold text-gray-800">{formatFileSize(fileStats.tamanio)} MB</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm border flex flex-col items-center justify-center">
                      <p className="text-sm text-gray-500">Palabras</p>
                      <p className="text-lg font-semibold text-gray-800">{fileStats.palabras}</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm border flex flex-col items-center justify-center">
                      <p className="text-sm text-gray-500">Caracteres</p>
                      <p className="text-lg font-semibold text-gray-800">{fileStats.caracteres}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Reproductor de Audio */}
              <AudioPlayer />

              {/* Mensaje de error */}
              {audioState.error && (
                <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
                  Error: {audioState.error}
                </div>
              )}

              {/* Botones de acción */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                {!audioState.audioUrl ? (
                  <button
                    onClick={() => handleExportToAudio(file.name)}
                    disabled={isUploading || audioState.isGenerating}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-8 rounded-lg transition duration-300 flex items-center justify-center"
                  >
                    {audioState.isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Generando audio...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m0-9.9a5 5 0 011.414-1.414M9 17.072a7 7 0 002.828-2.828M9 17.072V19a2 2 0 002 2h2a2 2 0 002-2v-1.928" />
                        </svg>
                        Exportar a audio
                      </>
                    )}
                  </button>
                ) : null}
                
                <button
                  onClick={() => handleDownloadText(file.name)}
                  disabled={isUploading}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-3 px-8 rounded-lg transition duration-300 flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Descargar solo texto
                </button>
              </div>
              
              <button
                onClick={() => {
                  setFile(null);
                  setFileStats(null);
                  setUploadMessage("");
                  setAudioState({
                    isGenerating: false,
                    audioUrl: null,
                    audioName: null,
                    error: null
                  });
                }}
                disabled={isUploading}
                className="mt-4 text-blue-600 hover:text-blue-800 disabled:text-gray-500 font-medium transition duration-300"
              >
                Cargar otro archivo
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;