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

        # --- CARGA ROBUSTA DE LLAVE ---
        llave_servidor = self._cargar_llave_servidor()
        
        if not llave_servidor:
            print("[ERROR CRÍTICO] No se pudo cargar la llave del servidor.")
            self.emisor = None 
            return 
        # ------------------------------

        config = ConfigRed(
            host_escucha="0.0.0.0", # Escuchar en todas las interfaces
            puerto_escucha=0,       # Puerto aleatorio
            host_destino=self.host_servidor,
            puerto_destino=self.puerto_servidor,
            llave_publica_destino=llave_servidor
        )

        self.receptor_interno = ReceptorCliente()

        try:
            print("[LogicaCliente] Ensamblando red...")
            self.emisor = self.ensamblador.ensamblar(self.receptor_interno, config)
            
            # AUMENTADO: Tiempo de espera vital para que el socket se abra correctamente
            time.sleep(1.0) 

            if self.ensamblador._servidor:
                self.mi_puerto = self.ensamblador._servidor.get_puerto()
                # FORZADO: Usar 127.0.0.1 para evitar problemas de resolución de nombres en local
                self.mi_host = "127.0.0.1"
                print(f"[LogicaCliente] Conectado. Escuchando en {self.mi_host}:{self.mi_puerto}")
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
            "host_escucha": self.mi_host, # ENVIAMOS LA IP CORRECTA
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
            "host_escucha": self.mi_host, # ENVIAMOS LA IP CORRECTA
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

    def _validar_conexion(self):
        if self.emisor is None:
            print("[ERROR] Intento de envío sin conexión válida (Falta llave o error de red)")
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