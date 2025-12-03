import threading
import json
import time
from ..DTOs.PaqueteDTO import PaqueteDTO
from ...Red.Emisor.ClienteTCP import ClienteTCP
from ...Red.Receptor.ServidorTCP import ServidorTCP
from ...Red.Cifrado.seguridad import GestorSeguridad
from ...Red.Receptor.ColaRecibos import ColaRecibos
from ...Red.Emisor.ColaEnvios import ColaEnvios

class LogicaCliente:
    def __init__(self):
        self.seguridad = GestorSeguridad()
        self.colaRecibos = ColaRecibos()
        self.cola_envios = ColaEnvios()

        self.host_servidor = "localhost"
        self.puerto_servidor = 5000

        self.mi_servidor = ServidorTCP(self.colaRecibos, self.seguridad,puerto_servidor=self, puerto=0, host="0.0.0.0")
        self.mi_servidor.iniciar()

        time.sleep(0.5)
        self.mi_puerto = self.mi_servidor.get_puerto()
        self.mi_host = "localhost"

        self.cliente_tcp = ClienteTCP(self.cola_envios, self.seguridad,None, self.host_servidor,self.puerto_servidor)

        self.usuario_actual = None
        self.callback_mensaje = None

        threading.Thread(target=self._procesar_recepcion, daemon=True).start()
    def set_callback(self,funcion):
        self.callback_mensaje = funcion

    def registrar(self, usuario, password):
        """envia solicitud de registro"""
        contenido = {"usuario": usuario, "password": password}
        self._enviar_paquete("REGISTRO", contenido)

    def login(self,usuario,password):
        """envia solicitud de login"""
        self.usuario_actual = usuario
        public_key_pem = self.seguridad.obtener_publica_bytes().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self,mensaje, destino="TODOS"):
        """envia un mensaje de chat"""
        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
        }
        self.enviar_paquete("MENSAJE", contenido,destino=destino)

    def _enviar_paquete(self,tipo,contenido,destino="SERVIDOR"):
        paquete = PaqueteDTO(
            tipo=tipo,
            contenido=contenido,
            origen=self.usuario_actual,
            destino=destino,
            host=self.host_servidor,
            puerto=self.puerto_servidor
        )
        if self.cliente_tcp.llave_destino is None:
            pass
        self.cola_envios.encolar(paquete)

    def _procesar_recepcion(self):
        """escucha la cola de recibos y actua"""
        while True:
            if not self.colaRecibos.esta_vacia():
                paquete = self.colaRecibos.desencolar()
                if paquete:
                    if self.callback_mensaje:
                        self.callback_mensaje(paquete)
            time.sleep(0.1)
gestor_cliente = LogicaCliente()