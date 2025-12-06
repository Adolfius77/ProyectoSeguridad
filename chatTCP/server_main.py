import sys
import os
import time
import logging

from src.ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO
from src.utils.generadorColor import GeneradorColor
from src.ConfigProperties.ConfigReader import ConfigReader

# --- Configuración de rutas ABSOLUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta chatTCP
project_root = os.path.dirname(current_dir)  # Raíz del proyecto
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)


from chatTCP.src.ComponenteReceptor.IReceptor import IReceptor
from chatTCP.src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from chatTCP.src.Red.Cifrado.seguridad import GestorSeguridad
from chatTCP.src.Datos.repositorio import repositorioUsuarios
from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

log_path = os.path.join(current_dir, 'servidor_bitacora.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - SERVER - %(message)s'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# Generador de color
generador_color = GeneradorColor()


class ReceptorLogicaServidor(IReceptor):
    """
    Receptor principal del SERVIDOR MAIN que:
      - Recibe conexiones de usuarios en puerto.entrada
      - Envía respuestas a usuarios usando puerto.salida
      - Envía eventos al EventBus (lista usuarios, mensajes, etc)
      - Mantiene login y registro intactos
    """
    def __init__(self, host_servidor, puerto_salida, host_bus, puerto_entrada_bus, ensamblador):
        # Configuración propia del servidor
        self.host_servidor = host_servidor
        self.puerto_salida = puerto_salida

        # Configuración del bus (para enviar eventos)
        self.host_bus = host_bus
        self.puerto_entrada_bus = puerto_entrada_bus

        self.ensamblador = ensamblador

    @property
    def cliente_tcp(self):
        return self.ensamblador._cliente_tcp

    @property
    def seguridad(self):
        return self.ensamblador._gestor_seguridad

    #   ENTRADA PRINCIPAL DE PAQUETES
    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        try:
            tipo = paquete.tipo
            logging.info(f"Procesando paquete: {tipo} de {paquete.origen}")

            if tipo == "REGISTRO":
                self._procesar_registro(paquete)

            elif tipo == "LOGIN":
                self._procesar_login(paquete)

            elif tipo == "MENSAJE":
                self._procesar_mensaje(paquete)

            elif tipo == "SOLICITAR_USUARIOS":
                self._enviar_lista_usuarios_al_bus()

        except Exception as e:
            logging.error(f"Error en logica servidor: {e}")

    #   REGISTRO
    def _procesar_registro(self, paquete):
        datos = paquete.contenido
        user = datos.get('usuario')
        pwd = datos.get('password')

        nuevo_usuario = UsuarioDTO(
            nombre_usuario=user,
            contrasena=pwd,
            ip=paquete.host,
            puerto=datos['puerto_escucha'],
            public_key=datos['public_key']
        )

        generador_color.asignar_color_a_usuario(nuevo_usuario)

        exito = repositorioUsuarios.guardar(nuevo_usuario)

        tipo_resp = "REGISTRO_OK" if exito else "REGISTRO_FAIL"
        msj = "Usuario creado correctamente" if exito else "El usuario ya existe"

        logging.info(f"Intento registro {user}: {tipo_resp}")

        self._enviar_respuesta_directa(
            paquete.host,
            datos['puerto_escucha'],
            datos['public_key'],
            tipo_resp,
            msj
        )

    #   LOGIN
    def _procesar_login(self, paquete):
        datos = paquete.contenido
        user = datos['usuario']

        logging.info(f"Intento login {user}")

        if repositorioUsuarios.validar(user, datos['password']):
            usuario_dto = repositorioUsuarios.obtener_usuario(user)
            usuario_sanitizado = usuario_dto.sin_contrasena()

            self._enviar_respuesta_directa(
                paquete.host,
                datos['puerto_escucha'],
                datos['public_key'],
                "LOGIN_OK",
                usuario_sanitizado.__dict__
            )

            # Notificar al EventBus
            self._enviar_lista_usuarios_al_bus()

        else:
            self._enviar_respuesta_directa(
                paquete.host,
                datos['puerto_escucha'],
                datos['public_key'],
                "ERROR",
                "Credenciales Incorrectas"
            )

    #   MENSAJE — SE ENVÍA SOLO AL EVENT BUS
    # ==========================================================
    def _procesar_mensaje(self, paquete):
        try:
            logging.info(f"Reenviando MENSAJE al Bus: {paquete.contenido}")

            paquete_bus = PaqueteDTO(
                tipo="MENSAJE",
                contenido=paquete.contenido,
                origen=paquete.origen,
                destino="EVENTBUS",
                host=self.host_bus,
                puerto_destino=self.puerto_entrada_bus
            )

            self.ensamblador.obtener_emisor().enviar_cambio(paquete_bus)

        except Exception as e:
            logging.error(f"Error reenviando mensaje al bus: {e}")

    #   LISTA DE USUARIOS — SOLO ENVÍA AL EVENT BUS
    def _enviar_lista_usuarios_al_bus(self):
        try:
            lista = [u.nombre_usuario for u in repositorioUsuarios.obtener_todos()]
            paquete_bus = PaqueteDTO(
                tipo="LISTA_USUARIOS",
                contenido=lista,
                origen="SERVIDOR",
                destino="EVENTBUS",
                host=self.host_bus,
                puerto_destino=self.puerto_entrada_bus
            )

            self.ensamblador.obtener_emisor().enviar_cambio(paquete_bus)
            logging.info("Lista de usuarios enviada al EventBus")

        except Exception as e:
            logging.error(f"Error enviando lista usuarios al bus: {e}")

    #   RESPUESTAS DIRECTAS A CLIENTES
    def _enviar_respuesta_directa(self, host, puerto, public_key_pem, tipo, contenido):
        try:
            llave = self.seguridad.importar_publica(public_key_pem.encode('utf-8'))
            self.cliente_tcp.llave_destino = llave
            paquete = PaqueteDTO(
                tipo,
                contenido,
                origen="SERVIDOR",
                destino="CLIENTE",
                host=host,
                puerto_destino=puerto
            )
            self.ensamblador.obtener_emisor().enviar_cambio(paquete)

        except Exception as e:
            logging.error(f"Error respondiendo directo: {e}")


#   SERVIDOR PRINCIPAL
class ServidorMain:
    def iniciar(self):
        print("=== SERVIDOR MAIN INICIADO ===")
        print(f"Directorio base: {current_dir}")

        self.ensamblador = EnsambladorRed.obtener_instancia()

        # Cargar o crear llaves persistentes del servidor
        ruta_llave_privada = os.path.join(current_dir, "server_private.pem")
        ruta_llave_publica = os.path.join(current_dir, "server_public.pem")

        # Crear gestor de seguridad
        self.seguridad = GestorSeguridad()

        if os.path.exists(ruta_llave_privada):
            # Cargar llaves existentes (sobrescribe las generadas automáticamente)
            if self.seguridad.cargar_privada_desde_archivo(ruta_llave_privada):
                print(f"✅ Llaves del servidor cargadas desde archivos existentes")
                # Verificar que se guardó la llave pública correspondiente
                llave_publica_pem = self.seguridad.obtener_publica_bytes()
                print(f"📍 Huella de llave pública: {llave_publica_pem[:50]}...")
            else:
                print(f"⚠️ Error al cargar llaves, usando llaves recién generadas y guardándolas...")
                self.seguridad.guardar_privada(ruta_llave_privada)
                self.seguridad.guardar_publica(ruta_llave_publica)
                print(f"✅ Llaves del servidor guardadas")
        else:
            # Guardar las llaves recién generadas
            self.seguridad.guardar_privada(ruta_llave_privada)
            self.seguridad.guardar_publica(ruta_llave_publica)
            print(f"✅ Llaves del servidor generadas y guardadas:")
            print(f"   - Privada: {ruta_llave_privada}")
            print(f"   - Pública: {ruta_llave_publica}")
            llave_publica_pem = self.seguridad.obtener_publica_bytes()
            print(f"📍 Huella de llave pública: {llave_publica_pem[:50]}...")

        self.ensamblador._gestor_seguridad = self.seguridad

        # Cargar configuración desde archivo .properties
        config_path = os.path.join(current_dir, 'config', 'config_ServidorMain.properties')
        try:
            config_reader = ConfigReader(config_path)

            # Configuración propia del servidor
            host_servidor = config_reader.obtener_str('host', 'localhost')
            puerto_entrada = config_reader.obtener_int('puerto.entrada', 6000)
            puerto_salida = config_reader.obtener_int('puerto.salida', 6001)

            # Configuración del bus (para enviarle eventos)
            host_bus = config_reader.obtener_str('hostBus', 'localhost')
            puerto_entrada_bus = config_reader.obtener_int('puerto.entradaBus', 5555)

            print(f"Configuración cargada desde: {config_path}")
            print(f"  Servidor Main:")
            print(f"    - Host: {host_servidor}")
            print(f"    - Puerto entrada (escucha usuarios): {puerto_entrada}")
            print(f"    - Puerto salida (responde usuarios): {puerto_salida}")
            print(f"  EventBus destino:")
            print(f"    - Host: {host_bus}")
            print(f"    - Puerto entrada: {puerto_entrada_bus}")
        except FileNotFoundError as e:
            print(f"Advertencia: {e}")
            print("Usando valores por defecto...")
            host_servidor = "localhost"
            puerto_entrada = 6000
            puerto_salida = 6001
            host_bus = "localhost"
            puerto_entrada_bus = 5555

        # Configuración del ensamblador de red
        # - Escucha en puerto_entrada para recibir de usuarios
        # - Envía al bus en host_bus:puerto_entrada_bus
        config = ConfigRed(
            host_escucha=host_servidor,
            puerto_escucha=puerto_entrada,
            host_destino=host_bus,
            puerto_destino=puerto_entrada_bus,
            llave_publica_destino=self.seguridad.public_key
        )

        # Guardar puerto de salida para respuestas a usuarios
        self.puerto_salida = puerto_salida
        self.host_servidor = host_servidor

        self.receptor_logica = ReceptorLogicaServidor(
            host_servidor,
            puerto_salida,
            host_bus,
            puerto_entrada_bus,
            self.ensamblador
        )

        self.ensamblador.ensamblar(self.receptor_logica, config)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo servidor...")
            self.ensamblador.detener()


if __name__ == "__main__":
    ServidorMain().iniciar()

