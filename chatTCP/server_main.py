import sys
import os
import time
import logging

from src.ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO
from src.utils.generadorColor import GeneradorColor

# --- Configuración de rutas ABSOLUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta chatTCP
project_root = os.path.dirname(current_dir)  # Raíz del proyecto
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)

from chatTCP.src.Bus.EventBus import EventBus
from chatTCP.src.Bus.ServicioDTO import ServicioDTO
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
      Procesa MENSAJES entre usuarios
      Envía LISTA_USUARIOS al EventBus (ya no existen subscriptores internos)
      Mantiene login y registro intactos
    """
    def __init__(self, host_bus, puerto_bus, ensamblador):
        self.host_bus = host_bus
        self.puerto_bus = puerto_bus
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
                puerto_destino=self.puerto_bus
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
                puerto_destino=self.puerto_bus
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
class ServidorBusApp:
    def iniciar(self):
        print("=== SERVIDOR MAIN INICIADO ===")
        print(f"Directorio base: {current_dir}")

        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.seguridad = GestorSeguridad()

        self.ensamblador._gestor_seguridad = self.seguridad

        # Cargar host/puerto del BUS desde archivo config
        host_bus = "localhost"
        puerto_bus = 5555

        # Configuración del servidor Main
        config = ConfigRed(
            host_escucha="0.0.0.0",
            puerto_escucha=6000,
            host_destino=host_bus,
            puerto_destino=puerto_bus,
            llave_publica_destino=self.seguridad.public_key
        )

        self.receptor_logica = ReceptorLogicaServidor(
            host_bus,
            puerto_bus,
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
    ServidorBusApp().iniciar()
