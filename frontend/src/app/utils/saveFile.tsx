// Enviar el archivo al backend
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });
    if (response.ok) {
      console.log('Archivo subido correctamente');
    }
  } catch (error) {
    console.error('Error al subir el archivo:', error);
  }
};

export default uploadFile;