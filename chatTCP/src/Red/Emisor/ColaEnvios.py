"""
Cola de envíos para paquetes de red
Implementa patrón Observer para notificar cuando hay datos disponibles
"""
from queue import Queue
from typing import Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..ObserverEmisor.ObservadorEnvios import ObservadorEnvios
    from ...ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO

from ..ObserverEmisor.ObservableEnvios import ObservableEnvios


class ColaEnvios(ObservableEnvios):
    """
    Cola que almacena paquetes para ser enviados por red
    Notifica a observadores cuando hay paquetes disponibles
    """

    def __init__(self):
        """
        Inicializa la cola de envíos
        """
        self._cola: Queue['PaqueteDTO'] = Queue()
        self._observador: Optional['ObservadorEnvios'] = None
        self._logger = logging.getLogger(__name__)

    def agregar_observador(self, observador: 'ObservadorEnvios') -> None:
        """
        Agrega un observador que será notificado cuando hay paquetes para enviar

        Args:
            observador: El observador a agregar
        """
        self._observador = observador
        self._logger.info(f"Observador agregado a ColaEnvios: {observador}")

    def notificar(self) -> None:
        """
        Notifica al observador que hay paquetes disponibles
        """
        if self._observador:
            self._logger.debug("Notificando observador de ColaEnvios")
            self._observador.actualizar()

    def encolar(self, paquete: 'PaqueteDTO') -> None:
        """
        Agrega un paquete a la cola y notifica al observador

        Args:
            paquete: El paquete a encolar
        """
        self._cola.put(paquete)
        self._logger.info(f"Paquete encolado para envío: {paquete}")
        self.notificar()

    def desencolar(self) -> Optional[str]:
        """
        Obtiene y serializa el siguiente paquete de la cola

        Returns:
            String JSON del paquete o None si la cola está vacía
        """
        if not self._cola.empty():
            paquete = self._cola.get()
            json_str = self._serializar(paquete)
            self._logger.debug(f"Paquete desencolado: {json_str}")
            return json_str
        return None

    def _serializar(self, paquete: 'PaqueteDTO') -> str:
        """
        Serializa un paquete a formato JSON

        Args:
            paquete: El paquete a serializar

        Returns:
            String JSON representando el paquete
        """
        return paquete.to_json()

    def esta_vacia(self) -> bool:
        """
        Verifica si la cola está vacía

        Returns:
            True si la cola está vacía, False en caso contrario
        """
        return self._cola.empty()

    def tamanio(self) -> int:
        """
        Obtiene el tamaño actual de la cola

        Returns:
            Número de paquetes en la cola
        """
        return self._cola.qsize()
