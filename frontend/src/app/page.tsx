"use client";
import React, { useState, useCallback } from "react";

interface FileStats {
  palabras: number;
  caracteres: number;
  tamanio: string;
}

interface AudioState {
  isGenerating: boolean;
  url: string | null;
  name: string | null;
  blob: Blob | null;
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
    url: null,
    name: null,
    blob:null,
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
          url: null,
          name: null,
          blob: null,
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
        url: null,
        name: null,
        blob:null,
        error: null
      });

      const response = await fetch(
        `http://localhost:5000/api/generar_audio?filename=procesado_${filename}`,
        {
          method: 'GET',
          mode: 'cors'
        }
      );

      if (response.ok) {            
          const audioBlob = await response.blob();
          
          // Crear una URL local para el blob
          const audioUrl = URL.createObjectURL(audioBlob);
          const audioName = `procesado_${filename.split('.')[0]}.ogg`;

          setAudioState({
            isGenerating: false,
            url: audioUrl,
            name: audioName,
            blob: audioBlob,
            error: null
          });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || `Error ${response.status}`);
      }
    } catch (error) {
      console.error('Error en la solicitud:', error);
      setAudioState({
        isGenerating: false,
        url: null,
        name: null,
        blob: null,
        error: error instanceof Error ? error.message : 'Error desconocido'
      });
    }
  }, []);

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

  const handleDownloadAudio = useCallback(async () => {
  if (audioState.url && audioState.name) {
    try {
      // Hacer una solicitud para obtener el blob del audio
      // const response = await fetch(audioState.audioUrl);
      
      // if (!response.ok) {
      //   throw new Error(`Error al obtener el audio: ${response.status}`);
      // }

      // // Convertir la respuesta a un blob
      // const audioBlob = await response.blob();
      
      // // Crear una URL local para el blob
      // const blobUrl = URL.createObjectURL(audioBlob);
      
      // Crear elemento anchor para descarga
      const a = document.createElement('a');
      a.href = audioState.url;
      
      // Usar el nombre del audio desde el estado o extraerlo de la URL
      const fileName = audioState.name;

      a.download = fileName;
      a.style.display = 'none';
      
      document.body.appendChild(a);
      a.click();
      
      document.body.removeChild(a);
      console.log("✅ Descarga iniciada correctamente");
      
    } catch (error) {
      console.error('❌ Error descargando audio:', error);
      
      // Fallback: abrir en nueva pestaña
      window.open(audioState.url, '_blank');
    }
  }
}, [audioState.url, audioState.name]);

  // Función para compartir en Telegram
  const handleShareTelegram = useCallback(async() => {
    if (!audioState.url) {
      alert('Primero debe generar el audio');
      return;
    }

    const botToken = process.env.NEXT_PUBLIC_TELEGRAM_BOT_TOKEN || '';
    const chatId = process.env.NEXT_PUBLIC_TELEGRAM_CHAT_ID || '';

    if (!botToken || !chatId) {
      console.error('Faltan variables de entorno para Telegram');
      alert('Error de configuración: Faltan credenciales de Telegram');
      return;
    }
    console.info('Compartiendo audio en Telegram...');
    console.info(audioState.name);
    console.info('Telegram Bot Token' + botToken);
    console.info('Telegram Chat' + chatId);

    const formData = new FormData();
    formData.append('chat_id', chatId);
    formData.append('audio', audioState.blob, audioState.name); 
    formData.append('performer', 'Tu App');
    formData.append('title', audioState.name.split('.')[0]);

    const options = {
      method: 'POST',
      body: formData
    };

    const response = await fetch(`https://api.telegram.org/bot${botToken}/sendAudio`, options);
    response.json().then(data => {
      if (data.ok) {
        console.log('Audio compartido en Telegram correctamente');
      } else {
        console.error('Error compartiendo audio en Telegram:', data);
      }
    }).catch(error => {
      console.error('Error procesando respuesta de Telegram:', error);
    });
        
    // window.open(telegramUrl, '_blank', 'width=600,height=400');
  }, [audioState.url, audioState.name, audioState.blob]);

  // Función para compartir en WhatsApp
  const handleShareWhatsApp = useCallback(() => {
    if (!audioState.url) {
      alert('Primero debe generar el audio');
      return;
    }

    const text = `¡Escucha este audio generado! ${audioState.url}`;
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
    window.open(whatsappUrl, '_blank', 'width=600,height=400');
  }, [audioState.url]);

  const AudioPlayer = () => {
    if (!audioState.url) return null;

    return (
      <div className="mt-6 p-4 bg-white rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Audio Generado</h3>
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <audio controls className="flex-1">
            <source src={audioState.url} type="audio/ogg" />
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

  // Componente para los botones de compartir flotantes
  const ShareButtons = () => {
    if (!audioState.url) return null;

    return (
      <div className="fixed bottom-6 right-6 flex flex-col gap-4 z-50">
        {/* Botón de WhatsApp */}
        <button
          onClick={handleShareWhatsApp}
          className="w-14 h-14 bg-green-500 hover:bg-green-600 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 transform hover:scale-110"
          title="Compartir en WhatsApp"
        >
          <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893-.001-3.189-1.262-6.209-3.553-8.485"/>
          </svg>
        </button>

        {/* Botón de Telegram */}
        <button
          onClick={handleShareTelegram}
          className="w-14 h-14 bg-blue-500 hover:bg-blue-600 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 transform hover:scale-110"
          title="Compartir en Telegram"
        >
          <svg className="w-12 h-12 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.157l-1.895 8.849c-.127.585-.465.73-.94.456l-2.609-1.92-1.258 1.212c-.139.135-.255.248-.511.248l.183-2.607 4.826-4.36c.205-.185-.045-.288-.318-.104l-5.961 3.752-2.57-.801c-.561-.174-.573-.561.117-.833l10.018-3.858c.467-.173.876.112.717.83z"/>
          </svg>
        </button>
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
                
                {/* {fileStats && (
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
                )} */}
              </div>

              {/* Mensaje de error */}
              {audioState.error && (
                <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
                  Error: {audioState.error}
                </div>
              )}

              {/* Reproductor de Audio */}
              <AudioPlayer />

              {/* Botones de acción */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                {!audioState.url ? (
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
                    url: null,
                    name: null,
                    blob: null,
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

      {/* Botones flotantes de compartir */}
      <ShareButtons />
    </div>
  );
};

export default App;