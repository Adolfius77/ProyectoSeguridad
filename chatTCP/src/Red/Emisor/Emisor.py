"""
Emisor principal para envío de paquetes
Implementa interfaz IEmisor
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ColaEnvios import ColaEnvios
    from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

from ...ComponenteEmisor.IEmisor import IEmisor


class Emisor(IEmisor):
    """
    Componente emisor que envía paquetes a través de la cola de envíos
    """

    def __init__(self, cola: 'ColaEnvios'):
        """
        Inicializa el emisor

        Args:
            cola: Cola de envíos donde se encolarán los paquetes
        """
        self._cola = cola
        self._logger = logging.getLogger(__name__)

    def enviar_cambio(self, paquete: 'PaqueteDTO') -> None:
        """
        Envía un paquete a través de la red

        Args:
            paquete: El paquete a enviar

        Raises:
            ValueError: Si el paquete es None
        """
        if paquete is None:
            self._logger.error("Intento de enviar paquete None")
            raise ValueError("El paquete no puede ser None")

        self._logger.info(f"Enviando paquete: {paquete}")
        self._cola.encolar(paquete)

    def get_cola(self) -> 'ColaEnvios':
        """
        Obtiene la cola de envíos

        Returns:
            Cola de envíos asociada
        """
        return self._cola
