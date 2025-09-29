import React, { useState, useCallback } from "react";

interface FileStats {
  size: string;
  words: number;
  characters: number;
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [fileStats, setFileStats] = useState<FileStats | null>(null);

  /**
   * Se dispara cuando un elemento arrastrado ENTREA al área de drop.
   */
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  /**
   * Se dispara cuando un elemento arrastrado SALE del área de drop.
   */
  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  /**
   * Es cargado un archivo finalmente por arrastre o por el input de carga
   */
  const handleFileChange = useCallback((selectedFile: File) => {
    if (!selectedFile) return;
    
    setFile(selectedFile);
    
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        // This is a simplified version - in a real app, you would need a library like mammoth.js
        // to properly parse Word documents, but we're simulating the functionality here
        const content = e.target?.result;
        const textContent = typeof content === 'string' ? content : '';
        
        // Simulate word and character count (in a real app, this would come from parsing the .docx file)
        const words = textContent.split(/\s+/).filter(word => word.length > 0).length;
        const characters = textContent.length;
        
        setFileStats({
          size: (selectedFile.size / (1024 * 1024)).toFixed(2),
          words: Math.floor(Math.random() * 1000) + 100, // Simulated word count
          characters: Math.floor(Math.random() * 5000) + 500, // Simulated character count
        });
      } catch (error) {
        console.error("Error processing file:", error);
      }
    };
    
    // For text files, we can read as text. For .docx, this won't work properly without a library
    if (selectedFile.type === 'text/plain') {
      reader.readAsText(selectedFile);
    } else {
      // Simulate processing for .docx files
      setTimeout(() => {
        setFileStats({
          size: (selectedFile.size / (1024 * 1024)).toFixed(2),
          words: Math.floor(Math.random() * 1000) + 100,
          characters: Math.floor(Math.random() * 5000) + 500,
        });
      }, 500);
    }
  }, []);
  
  /**
   * Se dispara cuando el usuario SUELTA (drop) el archivo sobre el área.
   */
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      if (selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.doc')) {
        handleFileChange(selectedFile);
      } else {
        alert('Por favor, seleccione un archivo Word (.doc o .docx)');
      }
    }
  }, [handleFileChange]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.docx') || selectedFile.name.endsWith('.doc')) {
        handleFileChange(selectedFile);
      } else {
        alert('Por favor, seleccione un archivo Word (.doc o .docx)');
      }
    }
  }, [handleFileChange]);

  const handleExportToAudio = () => {
    alert('Función de exportar a audio - En una implementación real, esto se comunicaría con el backend Python');
  };

  const handleDownloadText = async(filename: string) => {
    // Para descargar un archivo        
        const response = await fetch(`http://localhost:5000/api/descargar_doc_procesado?filename=${filename}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            console.error('Error al descargar el archivo');
        }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">Procesador de Documentos Word</h1>
          <p className="text-lg text-gray-600">Carga tu archivo Word para analizarlo y exportarlo</p>
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
              <p className="text-gray-500 mb-6">o</p>
              <label className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg cursor-pointer transition duration-300 inline-block">
                Seleccionar archivo
                <input 
                  type="file" 
                  accept=".doc,.docx" 
                  onChange={handleFileInput}
                  className="hidden"
                />
              </label>
              <p className="text-sm text-gray-500 mt-4">Formatos soportados: .doc, .docx</p>
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
                {fileStats && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 w-full max-w-md">
                    <div className="bg-white rounded-lg p-4 shadow-sm border">
                      <p className="text-sm text-gray-500">Tamaño</p>
                      <p className="text-lg font-semibold text-gray-800">{fileStats.size} MB</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm border">
                      <p className="text-sm text-gray-500">Palabras</p>
                      <p className="text-lg font-semibold text-gray-800">{fileStats.words}</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm border">
                      <p className="text-sm text-gray-500">Caracteres</p>
                      <p className="text-lg font-semibold text-gray-800">{fileStats.characters}</p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
                <button
                  onClick={handleExportToAudio}
                  className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-8 rounded-lg transition duration-300 flex items-center justify-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m0-9.9a5 5 0 011.414-1.414M9 17.072a7 7 0 002.828-2.828M9 17.072V19a2 2 0 002 2h2a2 2 0 002-2v-1.928" />
                  </svg>
                  Exportar a audio
                </button>
                <button
                  onClick={() => handleDownloadText(file.name)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-8 rounded-lg transition duration-300 flex items-center justify-center"
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
                }}
                className="mt-4 text-blue-600 hover:text-blue-800 font-medium transition duration-300"
              >
                Cargar otro archivo
              </button>
            </div>
          )}
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Nota: Esta es una demostración frontend. En una implementación real, se necesitaría un backend en Python para procesar archivos .docx y generar audio.</p>
        </div>
      </div>
    </div>
  );
};

export default App;