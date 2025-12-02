"""
EnsambladorBus: Ensamblador que inicializa y conecta todos los componentes del EventBus
"""
import logging
from typing import Optional

from .EventBus import EventBus
from .PublicadorEventos import PublicadorEventos
from ..Red.Emisor.ColaEnvios import ColaEnvios
from ..Red.Emisor.ClienteTCP import ClienteTCP
from ..Red.Emisor.Emisor import Emisor
from ..Red.Receptor.ColaRecibos import ColaRecibos
from ..Red.Receptor.ServidorTCP import ServidorTCP
from ..Red.Receptor.Receptor import Receptor
from ...config.config_bus import ConfigBus
from ..Red.Cifrado.seguridad import GestorSeguridad


class EnsambladorBus:
    """
    Ensamblador que inicializa el EventBus como servicio independiente
    """

    def __init__(self, config: Optional[ConfigBus] = None):
        """
        Inicializa el ensamblador

        Args:
            config: Configuración del bus (usa ConfigBus por defecto)
        """
        self._config = config or ConfigBus()
        self._event_bus: Optional[EventBus] = None
        self._servidor: Optional[ServidorTCP] = None
        self._logger = logging.getLogger(__name__)

        self.seguridad = GestorSeguridad()

        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, self._config.LOG_LEVEL),
            format=self._config.LOG_FORMAT
        )
        self.cola_envios = None
        self.cola_recibos = None

    def ensamblar(self) -> EventBus:
        """
        Ensambla e inicializa todos los componentes del EventBus

        Returns:
            Instancia del EventBus inicializada
        """
        self._logger.info("Iniciando ensamblaje del EventBus...")

        # 1. Crear cola de envíos
        cola_envios = ColaEnvios()
        self._logger.info("Cola de envíos creada")

        # 2. Crear cliente TCP (observador de la cola de envíos)
        cliente_tcp = ClienteTCP(
            cola=cola_envios,
            seguridad=self.seguridad,
            llave_destino=self.seguridad.public_key,
            host=self._config.HOST,
            puerto=self._config.PUERTO_BUS
        )
        self.cola_envios.agregar_observador(cliente_tcp)

        self._logger.info("Cliente TCP creado y conectado a cola de envíos")

        # 3. Crear emisor
        emisor = Emisor(self.cola_envios)
        self._logger.info("Emisor creado")

        # 4. Crear EventBus con el emisor
        self._event_bus = EventBus(
            emisor=emisor,
            puerto_bus=self._config.PUERTO_BUS
        )
        self._logger.info("EventBus creado")

        # 5. Crear cola de recibos
        self.cola_recibos = ColaRecibos()
        self._logger.info("Cola de recibos creada")

        # 6. Crear publicador de eventos (receptor que publica al EventBus)
        publicador = PublicadorEventos(
            event_bus=self._event_bus,
            host=self._config.HOST,
            puerto=self._config.PUERTO_ENTRADA
        )
        self._logger.info("Publicador de eventos creado")

        # 7. Crear receptor y conectarlo con el publicador
        receptor = Receptor()
        receptor.set_cola(self.cola_recibos)
        receptor.set_receptor(publicador)
        self.cola_recibos.agregar_observador(receptor)
        self._logger.info("Receptor creado y conectado")

        # 8. Crear servidor TCP (escucha en puerto de entrada)
        self._servidor = ServidorTCP(
            cola=self.cola_recibos,
            seguridad=self.seguridad,
            puerto=self._config.PUERTO_ENTRADA,
            host='0.0.0.0'  # Escuchar en todas las interfaces
        )
        self._logger.info(f"Servidor TCP creado en puerto {self._config.PUERTO_ENTRADA}")

        # 9. Iniciar servidor
        self._servidor.iniciar()
        self._logger.info("Servidor TCP iniciado")

        self._logger.info("Ensamblaje del EventBus completado exitosamente")
        return self._event_bus

    def detener(self) -> None:
        """
        Detiene el EventBus y todos sus componentes
        """
        self._logger.info("Deteniendo EventBus...")

        if self._servidor:
            self._servidor.detener()

        if self._event_bus:
            self._event_bus.limpiar_servicios()

        self._logger.info("EventBus detenido")

    def get_event_bus(self) -> Optional[EventBus]:
        """
        Obtiene la instancia del EventBus

        Returns:
            EventBus o None si no se ha ensamblado
        """
        return self._event_bus

    def get_servidor(self) -> Optional[ServidorTCP]:
        """
        Obtiene la instancia del servidor TCP

        Returns:
            ServidorTCP o None si no se ha ensamblado
        """
        return self._servidor


def main():
    """
    Función principal para ejecutar el EventBus como servicio independiente
    """
    print("=== EventBus - Servicio de Mensajería Distribuida ===")
    print("Inicializando...")

    ensamblador = EnsambladorBus()
    event_bus = ensamblador.ensamblar()

    config = ConfigBus()
    print(f"\nEventBus ejecutándose:")
    print(f"  - Puerto de entrada: {config.PUERTO_ENTRADA}")
    print(f"  - Puerto de salida: {config.PUERTO_BUS}")
    print(f"  - Host: {config.HOST}")
    print("\nPresione Ctrl+C para detener...")

    try:
        # Mantener el servicio ejecutándose
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nDeteniendo EventBus...")
        ensamblador.detener()
        print("EventBus detenido. Adiós!")


if __name__ == "__main__":
    main()
