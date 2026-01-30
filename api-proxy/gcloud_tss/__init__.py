from .client import GoogleCloudTTSClient
# from .auth.credentials import GoogleCloudCredentials
from .exceptions import GoogleCloudError, AuthenticationError, SynthesisError

__all__ = [
    'GoogleCloudTTSClient',
    # 'GoogleCloudCredentials',
    # exceptions
    'GoogleCloudError',
    'AuthenticationError',
    'SynthesisError'
]