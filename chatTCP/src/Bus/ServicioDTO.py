"""
DTO para representar un servicio de red (endpoint)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServicioDTO:
    """
    Representa un endpoint de red con host, puerto y llave pública RSA
    """
    id: int                   # ← ID entero
    host: str
    puerto: int
    llave_publica: Optional[bytes] = None  # Llave pública RSA en formato PEM

    def __str__(self) -> str:
        """
        Representación en string del servicio
        """
        return f"{self.host}:{self.puerto}"

    def __eq__(self, other) -> bool:
        """
        Compara dos servicios por ID (único)
        """
        if not isinstance(other, ServicioDTO):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Hash basado únicamente en el ID
        """
        return hash(self.id)
