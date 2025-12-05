"""
EnsambladorBus - Patrón Singleton para ensamblar el EventBus con la capa de Red.

Ensambla:
- EventBus (importado desde EventBus.py)
- EnsambladorRed (Singleton) para la capa de red
- PublicadorEventos como adaptador Red → EventBus

1. Crear EventBus
2. Ensamblar emisor del bus usando EnsambladorRed
3. Ensamblar receptor del bus usando EnsambladorRed + PublicadorEventos
4. Conectar todo
"""
# Ajustar sys.path para permitir ejecución directa
import sys
import os
from pathlib import Path

# Si se ejecuta directamente, agregar la raíz del proyecto al path
if __name__ == "__main__":
    # Obtener el directorio raíz del proyecto (chatTCP/)
    ruta_actual = Path(__file__).resolve()
    ruta_src = ruta_actual.parent.parent  # chatTCP/src/
    ruta_proyecto = ruta_src.parent  # chatTCP/

    # Agregar al sys.path si no está
    if str(ruta_proyecto) not in sys.path:
        sys.path.insert(0, str(ruta_proyecto))

from typing import Optional
from chatTCP.src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from chatTCP.src.ComponenteEmisor.IEmisor import IEmisor
from chatTCP.src.Bus.EventBus import EventBus
from chatTCP.src.Bus.PublicadorEventos import PublicadorEventos


class ConfigBus:
    """Configuración para el EnsambladorBus"""
    def __init__(
        self,
        host: str,
        puerto_entrada: int,
        puerto_bus: int,
        llave_publica_destino: Optional[bytes] = None
    ):
        """
        Args:
            host: Host del bus
            puerto_entrada: Puerto donde el bus escucha (recibe paquetes)
            puerto_bus: Puerto desde donde el bus envía paquetes
            llave_publica_destino: Llave pública del destino (opcional)
        """
        self.host = host
        self.puerto_entrada = puerto_entrada
        self.puerto_bus = puerto_bus
        self.llave_publica_destino = llave_publica_destino


class EnsambladorBus:
    """
    Ensamblador Singleton para el Bus de Eventos con integración de Red.

    Equivalente al EnsambladorBus de Java, pero usando EnsambladorRed
    para la capa de red en lugar de ensamblar componentes directamente.

    Uso:
        config = ConfigBus(
            host='localhost',
            puerto_entrada=5555,
            puerto_bus=5556
        )

        ensamblador = EnsambladorBus.obtener_instancia()
        event_bus = ensamblador.ensamblar(config)
    """

    _instancia: Optional['EnsambladorBus'] = None
    _inicializado: bool = False

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    @classmethod
    def obtener_instancia(cls) -> 'EnsambladorBus':
        """Obtiene la instancia única del ensamblador."""
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def __init__(self):
        """Inicialización del singleton (solo se ejecuta una vez)."""
        if EnsambladorBus._inicializado:
            return

        self._event_bus: Optional[EventBus] = None
        self._ensamblador_red: Optional[EnsambladorRed] = None
        self._publicador_eventos: Optional[PublicadorEventos] = None
        self._emisor: Optional[IEmisor] = None

        EnsambladorBus._inicializado = True

    def ensamblar(self, config: ConfigBus) -> EventBus:
        """
        Ensambla el EventBus con todos sus componentes de red.

        Equivalente al método iniciar() de Java:
        1. Crea el EventBus
        2. Ensambla el emisor del bus (usando EnsambladorRed)
        3. Ensambla el receptor del bus (usando EnsambladorRed + PublicadorEventos)
        4. Conecta EventBus con emisor
        5. Conecta Red con EventBus vía PublicadorEventos

        Args:
            config: Configuración del bus (host, puertos)

        Returns:
            EventBus: Instancia completamente ensamblada y en ejecución
        """
        # 1. Crear el EventBus
        self._event_bus = EventBus()

        # 2. Crear configuración de red
        # El bus escucha en puerto_entrada y envía desde puerto_bus
        config_red = ConfigRed(
            host_escucha='0.0.0.0',  # Escuchar en todas las interfaces
            puerto_escucha=config.puerto_entrada,
            host_destino=config.host,
            puerto_destino=config.puerto_bus,
            llave_publica_destino=config.llave_publica_destino
        )

        # 3. Obtener EnsambladorRed (Singleton)
        self._ensamblador_red = EnsambladorRed.obtener_instancia()

        # 4. Crear PublicadorEventos como receptor
        # Este adaptador recibe paquetes de la red y los publica en el EventBus
        self._publicador_eventos = PublicadorEventos(
            event_bus=self._event_bus,
            host=config.host,
            puerto=config.puerto_bus
        )

        # 5. Ensamblar la red con PublicadorEventos como receptor
        # Esto crea: ColaEnvios → ClienteTCP → Emisor
        # Y: ServidorTCP → ColaRecibos → Receptor → PublicadorEventos → EventBus
        self._emisor = self._ensamblador_red.ensamblar(
            receptor=self._publicador_eventos,
            config=config_red
        )

        # 6. Configurar el emisor en el EventBus
        self._event_bus.set_emisor(self._emisor)

        print(f"[EnsambladorBus] Bus ensamblado - Puerto entrada: {config.puerto_entrada}, Puerto bus: {config.puerto_bus}")

        return self._event_bus

    def obtener_event_bus(self) -> Optional[EventBus]:
        """
        Retorna el EventBus ensamblado (si existe).

        Returns:
            EventBus o None si no ha sido ensamblado
        """
        return self._event_bus

    def obtener_emisor(self) -> Optional[IEmisor]:
        """
        Retorna el emisor de red (si existe).

        Returns:
            IEmisor o None si no ha sido ensamblado
        """
        return self._emisor

    def obtener_llave_publica(self) -> Optional[bytes]:
        """
        Obtiene la llave pública del GestorSeguridad dentro de EnsambladorRed.

        Returns:
            Llave pública en formato PEM, o None si no está ensamblado
        """
        if self._ensamblador_red is None:
            return None
        return self._ensamblador_red.obtener_llave_publica()

    def detener(self):
        """Detiene el servidor de red y libera recursos."""
        if self._ensamblador_red is not None:
            self._ensamblador_red.detener()
            print("[EnsambladorBus] Bus detenido")

    @classmethod
    def resetear(cls):
        """Resetea el singleton (útil para testing)."""
        if cls._instancia is not None:
            cls._instancia.detener()
        cls._instancia = None
        cls._inicializado = False


def cargar_configuracion(archivo_config: str) -> ConfigBus:
    """
    Carga la configuración desde un archivo .properties

    Args:
        archivo_config: Ruta al archivo de configuración

    Returns:
        ConfigBus con la configuración cargada
    """
    import os
    from pathlib import Path

    # Si la ruta es relativa, buscar en config/
    if not os.path.isabs(archivo_config):
        # Buscar desde la raíz del proyecto chatTCP
        base_path = Path(__file__).parent.parent.parent
        archivo_config = base_path / "config" / archivo_config

    if not os.path.exists(archivo_config):
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {archivo_config}")

    props = {}
    with open(archivo_config, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            # Ignorar comentarios y líneas vacías
            if linea and not linea.startswith('#'):
                if '=' in linea:
                    key, value = linea.split('=', 1)
                    props[key.strip()] = value.strip()

    # Parsear propiedades
    host = props.get('host', 'localhost')
    puerto_entrada = int(props.get('puerto.entrada', '5555'))
    puerto_bus = int(props.get('puerto.bus', '5556'))

    return ConfigBus(
        host=host,
        puerto_entrada=puerto_entrada,
        puerto_bus=puerto_bus
    )


if __name__ == "__main__":
    """
    Punto de entrada principal para ejecutar el EnsambladorBus.

    Uso:
        python -m chatTCP.src.Bus.EnsambladorBus [archivo_config]

    Si no se especifica archivo, usa config_bus.properties por defecto.
    """
    import sys

    try:
        # Determinar archivo de configuración
        archivo_config = "config_bus.properties"
        if len(sys.argv) > 1:
            archivo_config = sys.argv[1]

        print(f"[EnsambladorBus] Cargando configuración desde: {archivo_config}")
        config = cargar_configuracion(archivo_config)

        print(f"[EnsambladorBus] Host: {config.host}")
        print(f"[EnsambladorBus] Puerto entrada: {config.puerto_entrada}")
        print(f"[EnsambladorBus] Puerto bus: {config.puerto_bus}")

        # Crear y ensamblar
        ensamblador = EnsambladorBus.obtener_instancia()
        event_bus = ensamblador.ensamblar(config)

        print("[EnsambladorBus] Servicio iniciado correctamente")
        print(f"[EnsambladorBus] Escuchando en puerto {config.puerto_entrada}")

        # Obtener y mostrar llave pública
        llave_publica = ensamblador.obtener_llave_publica()
        if llave_publica:
            print(f"[EnsambladorBus] Llave pública generada ({len(llave_publica)} bytes)")

        # Mantener el servicio corriendo
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[EnsambladorBus] Deteniendo servicio...")
            ensamblador.detener()
            print("[EnsambladorBus] Servicio detenido")

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR al iniciar el EventBus: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
