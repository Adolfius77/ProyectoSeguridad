"""
Interfaz Observer para envíos de red
"""
from abc import ABC, abstractmethod


class ObservadorEnvios(ABC):
    """
    Interfaz para observadores que reaccionan cuando hay datos disponibles para enviar
    """

    @abstractmethod
    def actualizar(self) -> None:
        """
        Método llamado cuando hay nuevos datos disponibles para enviar
        """
        pass
