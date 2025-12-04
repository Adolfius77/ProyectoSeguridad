import threading
import json
import time
import os
import sys
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

       
        self.host_bus = "localhost" 
        self.puerto_bus = 5555

      
        self.mi_servidor = ServidorTCP(self.colaRecibos, self.seguridad, puerto=0, host="0.0.0.0")
        self.mi_servidor.iniciar()

        time.sleep(0.5)
        self.mi_puerto = self.mi_servidor.get_puerto()
        self.mi_host = "localhost" 

        
        self.llave_servidor = None
        self._cargar_llave_bus()

        
        self.cliente_tcp = ClienteTCP(
            self.cola_envios, 
            self.seguridad, 
            self.llave_servidor, 
            self.host_bus, 
            self.puerto_bus
        )
        # Conectamos el observador
        self.cola_envios.agregar_observador(self.cliente_tcp)

        self.usuario_actual = None
        self.callback_mensaje = None

        threading.Thread(target=self._procesar_recepcion, daemon=True).start()

    def _cargar_llave_bus(self):
        """Busca y carga la llave pública generada por el EnsambladorBus"""
        try:
            posibles_rutas = [
                "server_public.pem",
                os.path.join(os.path.dirname(__file__), "..", "..", "server_public.pem"),
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "server_public.pem")
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    with open(ruta, "rb") as f:
                        llave_bytes = f.read()
                        self.llave_servidor = self.seguridad.importar_publica(llave_bytes)
                        print(f"LogicaCliente: Llave del Bus cargada desde {ruta}")
                        return

            print("ERROR: No se encontró 'server_public.pem'. Ejecuta el Bus primero.")

        except Exception as e:
            print(f"Error al cargar la llave pública: {e}")

    def set_callback(self, funcion):
        self.callback_mensaje = funcion

    def registrar(self, usuario, password):
        """
        Envía solicitud de registro.
        Nota: Esto depende de que haya un servicio de Autenticación escuchando en el Bus.
        """
        public_key_pem = self.seguridad.obtener_publica_bytes().decode('utf-8')
        
        contenido = {
            "usuario": usuario, 
            "password": password,
            "puerto_escucha": self.mi_puerto, 
            "public_key": public_key_pem      
        }
        self._enviar_paquete("REGISTRO", contenido, destino="BUS")

    def login(self, usuario, password):
        """
        Inicio de sesión = Suscripción al Bus
        """
        self.usuario_actual = usuario
        public_key_pem = self.seguridad.obtener_publica_bytes().decode('utf-8')

        temas_suscripcion = [
            "CHAT_GLOBAL",          
            f"MENSAJE_{usuario}",   
            f"RESPUESTA_{usuario}"  
        ]

        
        self._enviar_paquete(
            tipo="INICIAR_CONEXION", 
            contenido=temas_suscripcion, 
            destino="BUS"
        )
        
        
        if self.callback_mensaje:
            from ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO
            paquete_ok = PaqueteDTO("LOGIN_OK", usuario)
            self.callback_mensaje(paquete_ok)


    def enviar_mensaje(self, mensaje, destino="TODOS"):
        """
        Envía un mensaje usando el enrutamiento por Tópicos del Bus
        """

        if destino == "TODOS":
            tipo_evento = "CHAT_GLOBAL"
        else:
            tipo_evento = f"MENSAJE_{destino}" 

        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
        }
        
        
        self._enviar_paquete(tipo_evento, contenido, destino="BUS")

    def _enviar_paquete(self, tipo, contenido, destino="BUS"):
        """Empaqueta y encola para envío"""
        if self.llave_servidor is None:
            print(f"ERROR: No se puede enviar '{tipo}'. Sin llave del Bus.")
            return

        paquete = PaqueteDTO(
            tipo=tipo,
            contenido=contenido,
            origen=self.usuario_actual,
            destino=destino,
            host=self.host_bus,
            puerto_destino=self.puerto_bus,
            puerto_origen=self.mi_puerto 
        )

        self.cola_envios.encolar(paquete)

    def _procesar_recepcion(self):
        """Escucha la cola de recibos y notifica a la UI"""
        while True:
            if not self.colaRecibos.esta_vacia():
                paquete = self.colaRecibos.desencolar()
                if paquete:
                    if self.callback_mensaje:
                        self.callback_mensaje(paquete)
            time.sleep(0.1)

# Instancia global para ser usada por las interfaces
gestor_cliente = LogicaCliente()