// ✅ Mejor performance: El frontend descarga directamente del CDN de Google

// ✅ Escalabilidad: GCS maneja automáticamente el tráfico

// ✅ Costo reducido: No usas ancho de banda de tu backend

// ✅ Mantenibilidad: Código más simple y separación de responsabilidades

// ✅ Disponibilidad: Archivos siempre accesibles incluso si tu backend cae

// # Crear bucket (si no existe)
// gsutil mb gs://tu-bucket-audio

// # Configurar CORS para el bucket
// gsutil cors set cors-config.json gs://tu-bucket-audio

// # cors-config.json
// [
//   {
//     "origin": ["http://localhost:3000", "http://127.0.0.1:3000"],
//     "method": ["GET", "HEAD"],
//     "responseHeader": ["Content-Type", "Content-Disposition"],
//     "maxAgeSeconds": 3600
//   }
// ]

// Función para descargar el audio
const handleDownloadAudio = useCallback(async (audioUrl: string, audioName: string) => {
  try {
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = `${audioName}.wav`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Alternativa usando fetch para mayor control
    // const response = await fetch(audioUrl);
    // const blob = await response.blob();
    // const url = window.URL.createObjectURL(blob);
    // ... misma lógica de descarga
  } catch (error) {
    console.error('Error descargando audio:', error);
  }
}, []);


// En el return de tu componente React
// {audioState.audioUrl && (
//   <div>
//     <audio controls>
//       <source src={audioState.audioUrl} type="audio/wav" />
//       Tu navegador no soporta el elemento de audio.
//     </audio>
//     <button 
//       onClick={() => handleDownloadAudio(audioState.audioUrl!, audioState.audioName!)}
//       className="download-button"
//     >
//       Descargar Audio
//     </button>
//   </div>
// )}