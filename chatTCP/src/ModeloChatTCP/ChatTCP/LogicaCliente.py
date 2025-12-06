import threading
import time
import os
import sys

# Ajuste de path para imports (subir 3 niveles desde este archivo)
current_dir = os.path.dirname(os.path.abspath(__file__))
chat_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, chat_root)

from src.PaqueteDTO.PaqueteDTO import PaqueteDTO
from src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from src.ComponenteReceptor.IReceptor import IReceptor
from src.Red.Cifrado.seguridad import GestorSeguridad
from src.ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO


class ReceptorCliente(IReceptor):
    def __init__(self):
        self.callback = None

    def set_callback(self, funcion):
        self.callback = funcion

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        if self.callback:
            try:
                self.callback(paquete)
            except Exception as e:
                print(f"[ReceptorCliente] Error en callback de UI: {e}")
        else:
            print(f"[ReceptorCliente] Paquete recibido sin callback: {paquete.tipo}")


class LogicaCliente:
    """
    Lógica de negocio del cliente.
    Recibe la configuración de red desde el main (ArranqueProyecto).
    """
    def __init__(self, ensamblador, emisor, mi_puerto, host_servidor, puerto_servidor):
        """
        Inicializa la lógica del cliente con configuración de red.

        Args:
            ensamblador: Instancia del EnsambladorRed ya configurado
            emisor: Emisor de red ya inicializado
            mi_puerto: Puerto donde este cliente escucha
            host_servidor: Host del servidor destino
            puerto_servidor: Puerto del servidor destino
        """
        self.ensamblador = ensamblador
        self.emisor = emisor
        self.mi_puerto = mi_puerto
        self.host_servidor = host_servidor
        self.puerto_servidor = puerto_servidor
        self.gestor_seguridad = GestorSeguridad()

        # Crear receptor interno con callback
        self.receptor_interno = ReceptorCliente()
        self.receptor_interno.set_callback(self._procesar_paquete)

        # Usuario actual (se llenará después del login)
        self.usuario_actual: UsuarioDTO | None = None

        print(f"[LogicaCliente] Inicializado correctamente")
        print(f"[LogicaCliente] Mi puerto: {self.mi_puerto}")
        print(f"[LogicaCliente] Servidor destino: {self.host_servidor}:{self.puerto_servidor}")

    # PROCESADOR PRINCIPAL DEL CLIENTE
    def _procesar_paquete(self, paquete: PaqueteDTO):
        tipo = paquete.tipo
        contenido = paquete.contenido

        # LOGIN OK CREAR UsuarioDTO
        if tipo == "LOGIN_OK":
            print("[CLIENTE] Login correcto. Creando UsuarioDTO...")

            try:
                self.usuario_actual = UsuarioDTO(
                    nombre_usuario=contenido["nombre_usuario"],
                    contrasena="",  # No se envía
                    ip=contenido["ip"],
                    puerto=contenido["puerto"],
                    color=contenido["color"],
                    public_key=contenido["public_key"]
                )

                print(f"[CLIENTE] Usuario autenticado: {self.usuario_actual.nombre_usuario}")
                print(f"[CLIENTE] Color asignado: {self.usuario_actual.color}")

            except Exception as e:
                print(f"[CLIENTE] Error creando UsuarioDTO: {e}")

        # Se settea el usuario a Logica ChatTCP y se le muestra su menu de los users
    #     instanciar logicaChatTCP aqui ????


    # Para UI
    def set_callback(self, funcion):
        self.receptor_interno.set_callback(funcion)

    # ENVÍOS
    def registrar(self, usuario, password):
        if not self._validar_conexion(): return

        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem
        }
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        if not self._validar_conexion(): return

        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        if not self._validar_conexion(): return

        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual.nombre_usuario if self.usuario_actual else "ANONIMO"
        }
        self._enviar_paquete("MENSAJE", contenido, destino=destino)

    def obtener_usuarios(self):
        if not self._validar_conexion(): return
        print("Solicitando lista de usuarios...")
        self._enviar_paquete("SOLICITAR_USUARIOS", {})

    def _enviar_paquete(self, tipo, contenido, destino="SERVIDOR"):
        paquete = PaqueteDTO(
            tipo=tipo,
            contenido=contenido,
            origen=self.usuario_actual.nombre_usuario if isinstance(self.usuario_actual, UsuarioDTO) else "ANONIMO",
            destino=destino,
            host=self.host_servidor,
            puerto_destino=self.puerto_servidor
        )
        self.emisor.enviar_cambio(paquete)

    def _validar_conexion(self):
        if self.emisor is None:
            print("[ERROR] Intento de envío sin conexión válida (Falta llave o error de red)")
            return False
        return True

    # LLAVE SERVIDOR
    def _cargar_llave_servidor(self):
        ruta_pem = os.path.join(chat_root, "server_public.pem")
        print(f"[LogicaCliente] Buscando llave en: {ruta_pem}")

        if os.path.exists(ruta_pem):
            try:
                with open(ruta_pem, "rb") as f:
                    print(f"[LogicaCliente] Llave servidor cargada ÉXITO.")
                    return self.gestor_seguridad.importar_publica(f.read())
            except Exception as e:
                print(f"[LogicaCliente] Error leyendo llave: {e}")
                return None
        else:
            print(f"[LogicaCliente] NO SE ENCONTRÓ {ruta_pem}. Asegúrate de ejecutar el servidor primero.")
            return None


# Instancia global que se asigna desde usuario_main.py
gestor_cliente = None
