from dataclasses import dataclass
from typing import Optional

@dataclass
class GoogleCloudCredentials:
    """Contenedor inmutable para credenciales"""
    # configuro las credenciales a partir de mi key-json
    credentials_json: str = None
    # dejo abierta la posibilidad de autenticacion con project y token
    project_id: Optional[str] = None
    token: Optional[str] = None
    
    # def __post_init__(self):
    #     if not self.project_id:
    #         raise ValueError("project_id es requerido")