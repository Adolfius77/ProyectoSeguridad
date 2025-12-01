"""
Receptor principal para procesamiento de paquetes recibidos
Implementa patrón Observer
"""
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .ColaRecibos import ColaRecibos
    from ...ComponenteReceptor.IReceptor import IReceptor

from ..ObserverReceptor.ObservadorRecibos import ObservadorRecibos


class Receptor(ObservadorRecibos):
    """
    Componente receptor que procesa paquetes recibidos de la cola
    """

    def __init__(self):
        """
        Inicializa el receptor
        """
        self._cola: Optional['ColaRecibos'] = None
        self._receptor: Optional['IReceptor'] = None
        self._logger = logging.getLogger(__name__)

    def set_cola(self, cola: 'ColaRecibos') -> None:
        """
        Establece la cola de recibos a observar

        Args:
            cola: Cola de recibos
        """
        self._cola = cola
        self._logger.info(f"Cola de recibos establecida en Receptor")

    def set_receptor(self, receptor: 'IReceptor') -> None:
        """
        Establece el receptor que procesará los paquetes

        Args:
            receptor: Objeto que implementa IReceptor para procesar paquetes
        """
        self._receptor = receptor
        self._logger.info(f"Receptor establecido: {receptor}")

    def actualizar(self) -> None:
        """
        Método llamado cuando hay paquetes disponibles en la cola
        Desencola y procesa el paquete
        """
        if not self._cola or not self._receptor:
            self._logger.warning("Cola o receptor no configurado")
            return

        paquete = self._cola.desencolar()
        if paquete:
            try:
                self._logger.info(f"Procesando paquete recibido: {paquete}")
                self._receptor.recibir_cambio(paquete)
            except Exception as e:
                self._logger.error(f"Error al procesar paquete: {e}")

    def get_cola(self) -> Optional['ColaRecibos']:
        """
        Obtiene la cola de recibos

        Returns:
            Cola de recibos asociada o None
        """
        return self._cola

    def get_receptor(self) -> Optional['IReceptor']:
        """
        Obtiene el receptor configurado

        Returns:
            Receptor configurado o None
        """
        return self._receptor
