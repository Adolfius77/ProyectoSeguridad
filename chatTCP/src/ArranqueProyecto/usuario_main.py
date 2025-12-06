import sys
import os
import time
import logging

# --- Configuración de rutas ABSOLUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta ArranqueProyecto
src_dir = os.path.dirname(current_dir)  # Carpeta src
chat_root = os.path.dirname(src_dir)  # Carpeta chatTCP
project_root = os.path.dirname(chat_root)  # Raíz del proyecto

sys.path.insert(0, project_root)
sys.path.insert(0, chat_root)

from src.ConfigProperties.ConfigReader import ConfigReader
from src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from src.Red.Cifrado.seguridad import GestorSeguridad
from src.ModeloChatTCP.ChatTCP.LogicaCliente import LogicaCliente, ReceptorCliente

log_path = os.path.join(chat_root, 'usuario_bitacora.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - USUARIO - %(message)s'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


class UsuarioMain:
    """
    Clase principal del USUARIO que:
      - Carga configuración desde config_Usuario.properties
      - Configura el ensamblador de red
      - Inicializa LogicaCliente con los parámetros de red
    """
    def __init__(self):
        self.ensamblador = None
        self.gestor_seguridad = None
        self.receptor_cliente = None
        self.emisor = None
        self.logica_cliente = None
        self.mi_puerto = None

        # Datos de configuración
        self.host_usuario = None
        self.puerto_entrada = None
        self.puerto_salida = None
        self.host_servidor = None
        self.puerto_entrada_servidor = None
        self.host_bus = None
        self.puerto_entrada_bus = None

    def iniciar(self):
        """Inicializa el sistema del usuario"""
        print("=== USUARIO MAIN INICIADO ===")
        print(f"Directorio base: {chat_root}")

        # Cargar configuración desde archivo .properties
        if not self._cargar_configuracion():
            print("Error al cargar configuración. Abortando...")
            return False

        # Cargar llave del servidor
        llave_servidor = self._cargar_llave_servidor()
        if not llave_servidor:
            print("Error: No se pudo cargar la llave del servidor.")
            return False

        # Configurar ensamblador de red
        if not self._configurar_red(llave_servidor):
            print("Error al configurar red. Abortando...")
            return False

        # Crear LogicaCliente con los parámetros de red
        self._crear_logica_cliente()

        print("\nUsuario iniciado correctamente")
        print(f"   Puerto escucha: {self.mi_puerto}")
        print(f"   Conectado a servidor: {self.host_servidor}:{self.puerto_entrada_servidor}")
        return True

    def _cargar_configuracion(self):
        """Carga configuración desde config_Usuario.properties"""
        config_path = os.path.join(chat_root, 'config', 'config_Usuario.properties')

        try:
            config_reader = ConfigReader(config_path)

            # Configuración propia del usuario
            self.host_usuario = config_reader.obtener_str('host', 'localhost')
            self.puerto_entrada = config_reader.obtener_int('puerto.entrada', 8000)
            self.puerto_salida = config_reader.obtener_int('puerto.salida', 8001)

            # Configuración del servidor
            self.host_servidor = config_reader.obtener_str('hostServidor', 'localhost')
            self.puerto_entrada_servidor = config_reader.obtener_int('puerto.entradaServidor', 6000)

            # Configuración del bus
            self.host_bus = config_reader.obtener_str('hostBus', 'localhost')
            self.puerto_entrada_bus = config_reader.obtener_int('puerto.entradaBus', 5555)

            print(f"Configuración cargada desde: {config_path}")
            print(f"  Usuario:")
            print(f"    - Host: {self.host_usuario}")
            print(f"    - Puerto entrada: {self.puerto_entrada}")
            print(f"    - Puerto salida: {self.puerto_salida}")
            print(f"  Servidor destino:")
            print(f"    - Host: {self.host_servidor}")
            print(f"    - Puerto entrada: {self.puerto_entrada_servidor}")
            print(f"  Bus destino:")
            print(f"    - Host: {self.host_bus}")
            print(f"    - Puerto entrada: {self.puerto_entrada_bus}")

            return True

        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Usando valores por defecto...")
            self.host_usuario = "localhost"
            self.puerto_entrada = 8000
            self.puerto_salida = 8001
            self.host_servidor = "localhost"
            self.puerto_entrada_servidor = 6000
            self.host_bus = "localhost"
            self.puerto_entrada_bus = 5555
            return True
        except Exception as e:
            print(f"Error inesperado al cargar configuración: {e}")
            return False

    def _cargar_llave_servidor(self):
        """Carga la llave pública del servidor"""
        ruta_pem = os.path.join(chat_root, "server_public.pem")
        print(f"Buscando llave del servidor en: {ruta_pem}")

        if not os.path.exists(ruta_pem):
            print(f"NO SE ENCONTRÓ {ruta_pem}")
            return None

        try:
            self.gestor_seguridad = GestorSeguridad()
            with open(ruta_pem, "rb") as f:
                llave_bytes = f.read()
                llave = self.gestor_seguridad.importar_publica(llave_bytes)
                print("✅ Llave del servidor cargada correctamente")
                print(f"📍 Huella de llave pública del servidor: {llave_bytes[:50]}...")
                return llave
        except Exception as e:
            print(f"❌ Error leyendo llave del servidor: {e}")
            return None

    def _configurar_red(self, llave_servidor):
        """Configura el ensamblador de red"""
        try:
            self.ensamblador = EnsambladorRed.obtener_instancia()
            self.ensamblador._gestor_seguridad = self.gestor_seguridad

            # Configuración: escucha en puerto_entrada, envía al servidor
            config = ConfigRed(
                host_escucha=self.host_usuario,
                puerto_escucha=self.puerto_entrada,
                host_destino=self.host_servidor,
                puerto_destino=self.puerto_entrada_servidor,
                llave_publica_destino=llave_servidor
            )

            # Crear receptor cliente
            self.receptor_cliente = ReceptorCliente()

            # Ensamblar red
            print("Ensamblando red...")
            self.emisor = self.ensamblador.ensamblar(self.receptor_cliente, config)
            time.sleep(0.5)

            # Obtener puerto real asignado
            if self.ensamblador._servidor:
                self.mi_puerto = self.ensamblador._servidor.get_puerto()
                print(f"Red ensamblada. Mi puerto: {self.mi_puerto}")
            else:
                raise Exception("El servidor interno no se inició")

            return True

        except Exception as e:
            print(f"Error al configurar red: {e}")
            return False

    def _crear_logica_cliente(self):
        """Crea LogicaCliente pasándole los parámetros de red"""
        try:
            self.logica_cliente = LogicaCliente(
                ensamblador=self.ensamblador,
                emisor=self.emisor,
                mi_puerto=self.mi_puerto,
                host_servidor=self.host_servidor,
                puerto_servidor=self.puerto_entrada_servidor
            )
            print("LogicaCliente inicializada")

        except Exception as e:
            print(f" Error al crear LogicaCliente: {e}")
            self.logica_cliente = None

    def obtener_logica_cliente(self):
        """Retorna la instancia de LogicaCliente"""
        return self.logica_cliente

    def set_callback(self, funcion):
        """Permite que la UI registre un callback para recibir paquetes"""
        if self.logica_cliente:
            self.logica_cliente.set_callback(funcion)

    def detener(self):
        """Detiene el ensamblador de red"""
        if self.ensamblador:
            print("\nDeteniendo usuario...")
            self.ensamblador.detener()


# Instancia global
gestor_usuario = None


def main():
    """Función principal - Inicia el sistema y muestra la interfaz de login"""
    global gestor_usuario

    gestor_usuario = UsuarioMain()

    if not gestor_usuario.iniciar():
        print("No se pudo iniciar el usuario")
        return

    # Obtener LogicaCliente
    logica = gestor_usuario.obtener_logica_cliente()

    print("\n=== USUARIO LISTO ===")
    print("Mostrando interfaz de inicio de sesión...\n")

    # Asignar gestor_cliente globalmente para la interfaz
    import src.ModeloChatTCP.ChatTCP.LogicaCliente as modulo_logica
    modulo_logica.gestor_cliente = logica

    # Importar y ejecutar la interfaz de inicio de sesión
    try:
        import src.Presentacion.interfazInicioSesion
        # La interfaz se ejecuta con mainloop() automáticamente
    except KeyboardInterrupt:
        print("\nCerrando aplicación...")
        gestor_usuario.detener()
    except Exception as e:
        print(f"Error al cargar interfaz: {e}")
        gestor_usuario.detener()


if __name__ == "__main__":
    main()


