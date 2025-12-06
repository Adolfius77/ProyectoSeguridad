"""
Cola de recibos para paquetes de red
Implementa patrón Observer para notificar cuando se reciben datos
"""
from queue import Queue
from typing import List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..ObserverReceptor.ObservadorRecibos import ObservadorRecibos
    # CAMBIO: Usar ruta relativa o desde src para evitar error de modulo
    from src.PaqueteDTO.PaqueteDTO import PaqueteDTO

from ..ObserverReceptor.ObservableRecibos import ObservableRecibos
# CAMBIO: Corregido el import para que sea consistente
from src.PaqueteDTO.PaqueteDTO import PaqueteDTO


class ColaRecibos(ObservableRecibos):
    """
    Cola que almacena paquetes recibidos de la red
    Notifica a observadores cuando hay nuevos paquetes
    """

    def __init__(self):
        """
        Inicializa la cola de recibos
        """
        self._cola: Queue[str] = Queue()  # Cola de strings JSON
        self._observadores: List['ObservadorRecibos'] = []
        self._logger = logging.getLogger(__name__)

    def agregar_observador(self, observador: 'ObservadorRecibos') -> None:
        """
        Agrega un observador que será notificado cuando se reciben paquetes

        Args:
            observador: El observador a agregar
        """
        if observador not in self._observadores:
            self._observadores.append(observador)
            self._logger.info(f"Observador agregado a ColaRecibos: {observador}")

    def notificar(self) -> None:
        """
        Notifica a todos los observadores que hay paquetes recibidos
        """
        self._logger.debug(f"Notificando {len(self._observadores)} observadores")
        for observador in self._observadores:
            try:
                observador.actualizar()
            except Exception as e:
                self._logger.error(f"Error al notificar observador {observador}: {e}")

    def encolar(self, json_str: str) -> None:
        """
        Agrega un paquete JSON a la cola y notifica a los observadores

        Args:
            json_str: String JSON del paquete recibido
        """
        self._cola.put(json_str)
        self._logger.info(f"Paquete recibido encolado: {json_str[:100]}...")
        self.notificar()

    def desencolar(self) -> Optional['PaqueteDTO']:
        """
        Obtiene y deserializa el siguiente paquete de la cola

        Returns:
            PaqueteDTO deserializado o None si la cola está vacía
        """
        if not self._cola.empty():
            json_str = self._cola.get()
            paquete = self._deserializar(json_str)
            self._logger.debug(f"Paquete desencolado: {paquete}")
            return paquete
        return None

    def _deserializar(self, json_str: str) -> 'PaqueteDTO':
        """
        Deserializa un string JSON a PaqueteDTO

        Args:
            json_str: String JSON a deserializar

        Returns:
            Instancia de PaqueteDTO

        Raises:
            ValueError: Si el JSON no se puede deserializar
        """
        try:
            return PaqueteDTO.from_json(json_str)
        except Exception as e:
            self._logger.error(f"Error al deserializar paquete: {e}")
            raise ValueError(f"No se pudo deserializar el paquete: {e}")

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