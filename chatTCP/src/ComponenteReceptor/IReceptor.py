"""
Interfaz para componentes receptores de paquetes
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO


class IReceptor(ABC):
    """
    Interfaz que define el contrato para componentes que reciben paquetes por red
    """

    @abstractmethod
    def recibir_cambio(self, paquete: 'PaqueteDTO') -> None:
        """
        Procesa un paquete recibido de la red

        Args:
            paquete: El paquete recibido
        """
        pass
