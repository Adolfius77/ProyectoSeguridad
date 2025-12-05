"""
PublicadorEventos: Adaptador entre la red y el EventBus
Recibe paquetes de red y los publica en el EventBus
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .EventBus import EventBus
    from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

from ..ComponenteReceptor.IReceptor import IReceptor


class PublicadorEventos(IReceptor):
    """
    Adaptador que recibe paquetes de la red y los publica en el EventBus
    Implementa interfaz IReceptor para integrarse con la capa de red
    """

    def __init__(self, event_bus: 'EventBus', host: str = 'localhost', puerto: int = 5555):
        """
        Inicializa el publicador de eventos

        Args:
            event_bus: EventBus donde se publicarán los eventos
            host: Host del publicador
            puerto: Puerto del publicador
        """
        self._event_bus = event_bus
        self._host = host
        self._puerto = puerto
        self._logger = logging.getLogger(__name__)

        self._logger.info(f"PublicadorEventos inicializado en {host}:{puerto}")

    def recibir_cambio(self, paquete: 'PaqueteDTO') -> None:
        """
        Recibe un paquete de la red y lo publica en el EventBus

        Args:
            paquete: Paquete recibido de la red
        """
        if paquete is None:
            self._logger.warning("Paquete None recibido, ignorando")
            return

        self._logger.info(f"Publicando evento en EventBus: {paquete}")

        try:
            self._event_bus.publicar_evento(paquete)
        except Exception as e:
            self._logger.error(f"Error al publicar evento: {e}")
            raise

    def get_host(self) -> str:
        """
        Obtiene el host del publicador

        Returns:
            Host del publicador
        """
        return self._host

    def get_puerto(self) -> int:
        """
        Obtiene el puerto del publicador

        Returns:
            Puerto del publicador
        """
        return self._puerto

    def get_event_bus(self) -> 'EventBus':
        """
        Obtiene el EventBus asociado

        Returns:
            EventBus asociado
        """
        return self._event_bus
