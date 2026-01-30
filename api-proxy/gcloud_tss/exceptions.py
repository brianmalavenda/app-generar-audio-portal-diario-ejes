# Pongo los tipos de errores realacionados a Google Cloud

class GoogleCloudError(Exception):
    """Excepción base para errores de Google Cloud"""
    pass

class AuthenticationError(GoogleCloudError):
    """Error en la autenticación"""
    pass

class SynthesisError(GoogleCloudError):
    """Error en la síntesis de audio"""
    pass