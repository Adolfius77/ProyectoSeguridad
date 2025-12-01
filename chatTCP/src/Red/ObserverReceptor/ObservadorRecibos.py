"""
Interfaz Observer para recepción de red
"""
from abc import ABC, abstractmethod


class ObservadorRecibos(ABC):
    """
    Interfaz para observadores que reaccionan cuando se reciben datos de red
    """

    @abstractmethod
    def actualizar(self) -> None:
        """
        Método llamado cuando se reciben nuevos datos de la red
        """
        pass
