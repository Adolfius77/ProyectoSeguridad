import threading
import time
import os
import sys
import socket

# --- CONFIGURACIÓN DE RUTAS ROBUSTA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subir hasta encontrar la carpeta chatTCP
chat_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if chat_root not in sys.path:
    sys.path.insert(0, chat_root)

from src.PaqueteDTO.PaqueteDTO import PaqueteDTO
from src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from src.ComponenteReceptor.IReceptor import IReceptor
from src.Red.Cifrado.seguridad import GestorSeguridad

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
    def __init__(self):
        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.gestor_seguridad = GestorSeguridad()

        self.host_servidor = "127.0.0.1"
        self.puerto_servidor = 5555

        llave_servidor = self._cargar_llave_servidor()
        
        if not llave_servidor:
            print("[ERROR CRÍTICO] No se pudo cargar la llave del servidor.")
            self.emisor = None 
            return 

        # Escuchar en 127.0.0.1 para evitar WinError 10061
        config = ConfigRed(
            host_escucha="127.0.0.1", 
            puerto_escucha=0,       
            host_destino=self.host_servidor,
            puerto_destino=self.puerto_servidor,
            llave_publica_destino=llave_servidor
        )

        self.receptor_interno = ReceptorCliente()

        try:
            print("[LogicaCliente] Ensamblando red...")
            self.emisor = self.ensamblador.ensamblar(self.receptor_interno, config)
            time.sleep(1.0) 

            if self.ensamblador._servidor:
                self.mi_puerto = self.ensamblador._servidor.get_puerto()
                self.mi_host = "127.0.0.1"
                print(f"[LogicaCliente] LISTO. Escuchando en {self.mi_host}:{self.mi_puerto}")
            else:
                raise Exception("El servidor interno no se inició")

        except Exception as e:
            print(f"[LogicaCliente] ERROR al ensamblar red: {e}")
            self.emisor = None
            self.mi_puerto = 0
            self.mi_host = "127.0.0.1"

        self.usuario_actual = None

    def set_callback(self, funcion):
        self.receptor_interno.set_callback(funcion)

    def registrar(self, usuario, password):
        if not self._validar_conexion(): return

        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "host_escucha": self.mi_host,
            "public_key": public_key_pem
        }
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        if not self._validar_conexion(): return

        self.usuario_actual = usuario
        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "host_escucha": self.mi_host,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        if not self._validar_conexion(): return

        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
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
            origen=self.usuario_actual if self.usuario_actual else "ANONIMO",
import threading
import time
import os
import sys
import socket # Added for socket operations

# --- CONFIGURACIÓN DE RUTAS ROBUSTA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subir hasta encontrar la carpeta chatTCP
chat_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
if chat_root not in sys.path:
    sys.path.insert(0, chat_root)

from src.PaqueteDTO.PaqueteDTO import PaqueteDTO
from src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from src.ComponenteReceptor.IReceptor import IReceptor
from src.Red.Cifrado.seguridad import GestorSeguridad

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
    def __init__(self):
        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.gestor_seguridad = GestorSeguridad()

        self.host_servidor = "127.0.0.1"
        self.puerto_servidor = 5555

        llave_servidor = self._cargar_llave_servidor()
        
        if not llave_servidor:
            print("[ERROR CRÍTICO] No se pudo cargar la llave del servidor.")
            self.emisor = None 
            return 

        # Escuchar en 127.0.0.1 para evitar WinError 10061
        config = ConfigRed(
            host_escucha="127.0.0.1", 
            puerto_escucha=0,       
            host_destino=self.host_servidor,
            puerto_destino=self.puerto_servidor,
            llave_publica_destino=llave_servidor
        )

        self.receptor_interno = ReceptorCliente()

        try:
            print("[LogicaCliente] Ensamblando red...")
            self.emisor = self.ensamblador.ensamblar(self.receptor_interno, config)
            time.sleep(1.0) 

            if self.ensamblador._servidor:
                self.mi_puerto = self.ensamblador._servidor.get_puerto()
                self.mi_host = "127.0.0.1"
                print(f"[LogicaCliente] LISTO. Escuchando en {self.mi_host}:{self.mi_puerto}")
            else:
                raise Exception("El servidor interno no se inició")

        except Exception as e:
            print(f"[LogicaCliente] ERROR al ensamblar red: {e}")
            self.emisor = None
            self.mi_puerto = 0
            self.mi_host = "127.0.0.1"

        self.usuario_actual = None

    def set_callback(self, funcion):
        self.receptor_interno.set_callback(funcion)

    def registrar(self, usuario, password):
        if not self._validar_conexion(): return

        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "host_escucha": self.mi_host,
            "public_key": public_key_pem
        }
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        if not self._validar_conexion(): return

        self.usuario_actual = usuario
        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "host_escucha": self.mi_host,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        if not self._validar_conexion(): return

        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
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
            origen=self.usuario_actual if self.usuario_actual else "ANONIMO",
            destino=destino,
            host=self.host_servidor,
            puerto_destino=self.puerto_servidor
        )
        self.emisor.enviar_cambio(paquete)

    def verificar_estado_servidor(self):
        """Intenta conectar al servidor para verificar si está activo"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.host_servidor, self.puerto_servidor))
                return result == 0
        except:
            return False

    def _validar_conexion(self):
        if self.emisor is None:
            print("[ERROR] Intento de envío sin conexión válida")
            return False
        
        # Verificar si el servidor está escuchando realmente
        if not self.verificar_estado_servidor():
            print("[ERROR] El servidor no parece estar respondiendo (WinError 10061)")
            # Podríamos notificar a la UI aquí si tuviéramos un callback de error global
            return False
            
        return True

    def _cargar_llave_servidor(self):
        ruta_pem = os.path.join(chat_root, "server_public.pem")
        if os.path.exists(ruta_pem):
            try:
                with open(ruta_pem, "rb") as f:
                    return self.gestor_seguridad.importar_publica(f.read())
            except Exception as e:
                print(f"[LogicaCliente] Error leyendo llave: {e}")
                return None
        else:
            print(f"[LogicaCliente] NO SE ENCONTRÓ {ruta_pem}.")
            return None

gestor_cliente = LogicaCliente()