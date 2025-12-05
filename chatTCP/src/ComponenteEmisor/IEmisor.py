"""
Interfaz para componentes emisores de paquetes
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO


class IEmisor(ABC):
    """
    Interfaz que define el contrato para componentes que envían paquetes por red
    """

    @abstractmethod
    def enviar_cambio(self, paquete: 'PaqueteDTO') -> None:
        """
        Envía un paquete a través de la red

        Args:
            paquete: El paquete a enviar
        """
        pass
