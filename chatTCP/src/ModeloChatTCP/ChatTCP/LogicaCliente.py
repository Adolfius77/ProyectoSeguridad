import threading
import json
import time
import os
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

        self.mi_servidor = ServidorTCP(self.colaRecibos, self.seguridad, puerto=0, host="0.0.0.0")
        self.mi_servidor.iniciar()

        time.sleep(0.5)
        self.mi_puerto = self.mi_servidor.get_puerto()
        self.mi_host = "localhost"

        llave_servidor = None
        try:
            if os.path.exists("server_public.pem"):
                with open("server_public.pem", "rb") as f:
                    llave_bytes = f.read()
                    llave_servidor = self.seguridad.importar_publica(llave_bytes)
            else:
                print(
                    "ADVERTENCIA: No se encontro 'server_public.pem'. El cliente no podra cifrar mensajes hacia el servidor.")
        except Exception as e:
            print(f"Error al cargar la llave publica del servidor: {e}")

        self.cliente_tcp = ClienteTCP(self.cola_envios, self.seguridad, llave_servidor, self.host_servidor,
                                      self.puerto_servidor)

        self.usuario_actual = None
        self.callback_mensaje = None

        # Hilo para procesar recibos (mensajes entrantes)
        threading.Thread(target=self._procesar_recepcion, daemon=True).start()

    def set_callback(self, funcion):
        self.callback_mensaje = funcion

    def registrar(self, usuario, password):
        """Envia solicitud de registro"""
        contenido = {"usuario": usuario, "password": password}
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        """Envia solicitud de login"""
        self.usuario_actual = usuario
        public_key_pem = self.seguridad.obtener_publica_bytes().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        """Envia un mensaje de chat"""
        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
        }
        self._enviar_paquete("MENSAJE", contenido, destino=destino)

    def _enviar_paquete(self, tipo, contenido, destino="SERVIDOR"):
        paquete = PaqueteDTO(
            tipo=tipo,
            contenido=contenido,
            origen=self.usuario_actual,
            destino=destino,
            host=self.host_servidor,
            puerto_destino=self.puerto_servidor
        )


        if self.cliente_tcp.llave_destino is None:
            print(f"ERROR: No se puede enviar el paquete '{tipo}'. Falta la llave pública del servidor.")
            return

        self.cola_envios.encolar(paquete)

    def _procesar_recepcion(self):
        """Escucha la cola de recibos y actúa"""
        while True:
            if not self.colaRecibos.esta_vacia():
                paquete = self.colaRecibos.desencolar()
                if paquete:
                    if self.callback_mensaje:
                        self.callback_mensaje(paquete)
            time.sleep(0.1)


# Instancia global para ser usada por las interfaces gráficas
gestor_cliente = LogicaCliente()