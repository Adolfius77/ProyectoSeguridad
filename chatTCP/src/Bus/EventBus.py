"""
EventBus: Bus de eventos centralizado para comunicación pub-sub
"""
import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from ..ComponenteEmisor.IEmisor import IEmisor
    from ..ModeloChatTCP.DTOs.ServicioDTO import ServicioDTO
    from ..ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO


class EventBus:
    """
    Bus de eventos centralizado que maneja registro de servicios y distribución de eventos
    Implementa patrón Publish-Subscribe
    """

    EVENTO_INICIAR_CONEXION = "INICIAR_CONEXION"

    def __init__(self, emisor: 'IEmisor', puerto_bus: int = 5556):
        """
        Inicializa el EventBus

        Args:
            emisor: Emisor para enviar paquetes a servicios registrados
            puerto_bus: Puerto desde el cual el bus enviará mensajes
        """
        self._servicios: Dict[str, List['ServicioDTO']] = defaultdict(list)
        self._emisor = emisor
        self._puerto_bus = puerto_bus
        self._logger = logging.getLogger(__name__)

        self._logger.info(f"EventBus inicializado en puerto {puerto_bus}")

    def publicar_evento(self, paquete: 'PaqueteDTO') -> None:
        """
        Procesa y distribuye un evento recibido

        Args:
            paquete: Paquete a procesar y distribuir
        """
        if paquete.tipo == self.EVENTO_INICIAR_CONEXION:
            self._registrar_servicio_desde_paquete(paquete)
        else:
            self._notificar_servicios(paquete)

    def registrar_servicio(self, tipo_evento: str, servicio: 'ServicioDTO') -> None:
        """
        Registra un servicio para un tipo de evento específico

        Args:
            tipo_evento: Tipo de evento al que se suscribe
            servicio: Servicio a registrar
        """
        if servicio not in self._servicios[tipo_evento]:
            self._servicios[tipo_evento].append(servicio)
            self._logger.info(f"Servicio {servicio} registrado para evento '{tipo_evento}'")
        else:
            self._logger.warning(f"Servicio {servicio} ya registrado para '{tipo_evento}'")

    def eliminar_servicio(self, tipo_evento: str, servicio: 'ServicioDTO') -> None:
        """
        Elimina un servicio de un tipo de evento

        Args:
            tipo_evento: Tipo de evento del cual eliminar
            servicio: Servicio a eliminar
        """
        if tipo_evento in self._servicios and servicio in self._servicios[tipo_evento]:
            self._servicios[tipo_evento].remove(servicio)
            self._logger.info(f"Servicio {servicio} eliminado de evento '{tipo_evento}'")

    def _registrar_servicio_desde_paquete(self, paquete: 'PaqueteDTO') -> None:
        """
        Registra un servicio desde un paquete INICIAR_CONEXION

        Args:
            paquete: Paquete con información de registro
        """
        from ..ModeloChatTCP.DTOs.ServicioDTO import ServicioDTO

        # El contenido debe ser una lista de tipos de eventos
        if not isinstance(paquete.contenido, list):
            self._logger.error(f"Contenido de INICIAR_CONEXION debe ser lista: {paquete.contenido}")
            return

        # Crear servicio desde datos del paquete
        servicio = ServicioDTO(
            host=paquete.host or 'localhost',
            puerto=paquete.puerto_origen
        )

        # Registrar servicio para cada tipo de evento
        for tipo_evento in paquete.contenido:
            self.registrar_servicio(tipo_evento, servicio)

        self._logger.info(f"Servicio {servicio} registrado para {len(paquete.contenido)} eventos")

    def _notificar_servicios(self, paquete: 'PaqueteDTO') -> None:
        """
        Notifica a todos los servicios suscritos a un tipo de evento

        Args:
            paquete: Paquete a distribuir
        """
        tipo_evento = paquete.tipo
        servicios = self._servicios.get(tipo_evento, [])

        if not servicios:
            self._logger.warning(f"No hay servicios registrados para evento '{tipo_evento}'")
            return

        self._logger.info(f"Distribuyendo evento '{tipo_evento}' a {len(servicios)} servicios")

        # Enviar a todos los servicios excepto el origen
        for servicio in servicios:
            # Evitar enviar al origen (si coincide el puerto)
            if paquete.puerto_origen and servicio.puerto == paquete.puerto_origen:
                self._logger.debug(f"Omitiendo envío al origen: {servicio}")
                continue

            # Normalizar paquete con información de destino
            paquete_normalizado = self._normalizar_paquete(paquete, servicio)

            try:
                self._emisor.enviar_cambio(paquete_normalizado)
                self._logger.debug(f"Evento enviado a {servicio}")
            except Exception as e:
                self._logger.error(f"Error al enviar evento a {servicio}: {e}")

    def _normalizar_paquete(self, paquete: 'PaqueteDTO', servicio: 'ServicioDTO') -> 'PaqueteDTO':
        """
        Completa información faltante en el paquete para envío

        Args:
            paquete: Paquete original
            servicio: Servicio destino

        Returns:
            Nuevo paquete con información completa
        """
        from ..ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO

        return PaqueteDTO(
            tipo=paquete.tipo,
            contenido=paquete.contenido,
            origen=paquete.origen,
            destino=servicio.host,
            host=servicio.host,
            puerto_origen=self._puerto_bus,
            puerto_destino=servicio.puerto
        )

    def obtener_servicios(self, tipo_evento: str) -> List['ServicioDTO']:
        """
        Obtiene todos los servicios registrados para un tipo de evento

        Args:
            tipo_evento: Tipo de evento

        Returns:
            Lista de servicios registrados
        """
        return self._servicios.get(tipo_evento, []).copy()

    def obtener_todos_servicios(self) -> Dict[str, List['ServicioDTO']]:
        """
        Obtiene todos los servicios registrados

        Returns:
            Diccionario de tipo_evento -> lista de servicios
        """
        return dict(self._servicios)

    def limpiar_servicios(self) -> None:
        """
        Elimina todos los servicios registrados
        """
        self._servicios.clear()
        self._logger.info("Todos los servicios han sido eliminados")
