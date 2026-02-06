"""
gcloud_tts: Cliente para Text-to-Speech de Google Cloud.

Paquete para sintetizar texto a audio usando Google Cloud TTS.
"""

__version__ = "1.0.0"
__author__ = "Brian Malavenda"
__license__ = "MIT"


from .client import GoogleCloudTTSClient
from .exceptions import (
    GoogleCloudError,
    AuthenticationError,
    SynthesisError
)

# Exportar API pública
__all__ = [
    'GoogleCloudTTSClient',
    'GoogleCloudCredentials',
    # exceptions
    'GoogleCloudError',
    'AuthenticationError',
    'SynthesisError'
]

# Metadata
__package_name__ = "gcloud_tts"
__description__ = "Cliente para Text-to-Speech de Google Cloud"
__url__ = "https://github.com/brianmalavenda/gcloud_tts"
__keywords__ = ["google-cloud", "text-to-speech", "tts", "audio"]