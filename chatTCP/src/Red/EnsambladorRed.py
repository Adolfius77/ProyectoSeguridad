"""
Ensamblador de componentes de red con patrón Singleton.
Ensambla toda la infraestructura de red TCP con cifrado.
"""
from typing import Optional
from dataclasses import dataclass
from ..ComponenteReceptor.IReceptor import IReceptor
from ..ComponenteEmisor.IEmisor import IEmisor
from .Emisor.ColaEnvios import ColaEnvios
from .Emisor.ClienteTCP import ClienteTCP
from .Emisor.Emisor import Emisor
from .Receptor.ColaRecibos import ColaRecibos
from .Receptor.ServidorTCP import ServidorTCP
from .Receptor.Receptor import Receptor
from .Cifrado.seguridad import GestorSeguridad


class ConfigRed:
    """Configuración para el ensamblador de red"""
    def __init__(
        self,
        host_escucha: str = '0.0.0.0',
        puerto_escucha: int = 5555,
        host_destino: str = 'localhost',
        puerto_destino: int = 5555,
        llave_publica_destino: Optional[bytes] = None
    ):
        self.host_escucha = host_escucha
        self.puerto_escucha = puerto_escucha
        self.host_destino = host_destino
        self.puerto_destino = puerto_destino
        self.llave_publica_destino = llave_publica_destino


class EnsambladorRed:
    """
    Ensamblador Singleton para componentes de red TCP.

    Ensambla:
    - Sistema de emisión: ColaEnvios + ClienteTCP + Emisor
    - Sistema de recepción: ColaRecibos + ServidorTCP + Receptor
    - Sistema de seguridad: GestorSeguridad

    Uso:
        config = ConfigRed(puerto_escucha=5555, puerto_destino=5556)
        ensamblador = EnsambladorRed.obtener_instancia()
        emisor = ensamblador.ensamblar(receptor, config)
    """

    _instancia: Optional['EnsambladorRed'] = None
    _inicializado: bool = False

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    @classmethod
    def obtener_instancia(cls) -> 'EnsambladorRed':
        """Obtiene la instancia única del ensamblador"""
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def __init__(self):
        """Inicialización del singleton (solo se ejecuta una vez)"""
        if EnsambladorRed._inicializado:
            return

        self._emisor: Optional[IEmisor] = None
        self._servidor: Optional[ServidorTCP] = None
        self._gestor_seguridad: Optional[GestorSeguridad] = None
        self._cliente_tcp: Optional[ClienteTCP] = None

        EnsambladorRed._inicializado = True

    def ensamblar(
        self,
        receptor: IReceptor,
        config: ConfigRed
    ) -> IEmisor:
        """
        Ensambla todos los componentes de red.

        Args:
            receptor: Componente que procesará los paquetes recibidos
            config: Configuración de red (puertos, hosts, llave pública)

        Returns:
            IEmisor: Componente para enviar paquetes a través de la red
        """
        # Si ya fue ensamblado, detener componentes previos
        if self._servidor is not None:
            self._servidor.detener()

        # 1. Crear gestor de seguridad SOLO si no existe
        if self._gestor_seguridad is None:
            self._gestor_seguridad = GestorSeguridad()

        # 2. Ensamblar sistema de EMISIÓN
        cola_envios = ColaEnvios()

        # Si no hay llave pública destino, usar la propia (para testing/loopback)
        llave_destino = config.llave_publica_destino
        if llave_destino is None:
            llave_destino = self._gestor_seguridad.obtener_publica_bytes()

        self._cliente_tcp = ClienteTCP(
            cola=cola_envios,
            seguridad=self._gestor_seguridad,
            llave_destino=llave_destino,
            host=config.host_destino,
            puerto=config.puerto_destino
        )

        cola_envios.agregar_observador(self._cliente_tcp)

        self._emisor = Emisor(cola_envios)

        # 3. Ensamblar sistema de RECEPCIÓN
        cola_recibos = ColaRecibos()

        receptor_observador = Receptor()
        receptor_observador.set_cola(cola_recibos)
        receptor_observador.set_receptor(receptor)

        cola_recibos.agregar_observador(receptor_observador)

        self._servidor = ServidorTCP(
            cola=cola_recibos,
            seguridad=self._gestor_seguridad,
            puerto=config.puerto_escucha,
            host=config.host_escucha
        )

        # 4. Iniciar servidor
        self._servidor.iniciar()

        return self._emisor

    def obtener_emisor(self) -> Optional[IEmisor]:
        """Retorna el emisor ensamblado (si existe)"""
        return self._emisor

    def obtener_llave_publica(self) -> Optional[bytes]:
        """Retorna la clave pública del gestor de seguridad"""
        if self._gestor_seguridad is None:
            return None
        return self._gestor_seguridad.obtener_publica_bytes()

    def detener(self):
        """Detiene el servidor TCP"""
        if self._servidor is not None:
            self._servidor.detener()

    @classmethod
    def resetear(cls):
        """Resetea el singleton (útil para testing)"""
        if cls._instancia is not None and cls._instancia._servidor is not None:
            cls._instancia._servidor.detener()
        cls._instancia = None
        cls._inicializado = False
