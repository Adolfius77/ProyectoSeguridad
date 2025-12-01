"""
DTO para representar un servicio de red (endpoint)
"""
from dataclasses import dataclass


@dataclass
class ServicioDTO:
    """
    Representa un endpoint de red con host y puerto
    """
    host: str
    puerto: int

    def __str__(self) -> str:
        """
        Representación en string del servicio

        Returns:
            String en formato host:puerto
        """
        return f"{self.host}:{self.puerto}"

    def __eq__(self, other) -> bool:
        """
        Compara dos servicios por host y puerto

        Args:
            other: Otro servicio a comparar

        Returns:
            True si son iguales, False en caso contrario
        """
        if not isinstance(other, ServicioDTO):
            return False
        return self.host == other.host and self.puerto == other.puerto

    def __hash__(self) -> int:
        """
        Genera hash del servicio para uso en conjuntos y diccionarios

        Returns:
            Hash basado en host y puerto
        """
        return hash((self.host, self.puerto))
