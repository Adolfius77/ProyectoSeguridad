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

    
        self.host_servidor = "localhost" 
        self.puerto_servidor = 5000

       
        self.mi_servidor = ServidorTCP(self.colaRecibos, self.seguridad, puerto=0, host="0.0.0.0")
        self.mi_servidor.iniciar()

        time.sleep(0.5)
        self.mi_puerto = self.mi_servidor.get_puerto()
        self.mi_host = "localhost"

        llave_servidor = None
        try:
           
            ruta_actual = os.path.dirname(os.path.abspath(__file__))
          
            ruta_raiz = os.path.abspath(os.path.join(ruta_actual, "..", "..", ".."))
            
        
            ruta_pem = os.path.join(ruta_raiz, "server_public.pem")
            
            print(f"Buscando llave en: {ruta_pem}") 

            if os.path.exists(ruta_pem):
                with open(ruta_pem, "rb") as f:
                    llave_bytes = f.read()
                    llave_servidor = self.seguridad.importar_publica(llave_bytes)
                    print("LogicaCliente: Llave del servidor cargada EXITOSAMENTE.")
            else:
                
                if os.path.exists("server_public.pem"):
                    with open("server_public.pem", "rb") as f:
                        llave_bytes = f.read()
                        llave_servidor = self.seguridad.importar_publica(llave_bytes)
                        print("LogicaCliente: Llave cargada desde carpeta actual.")
                else:
                    print("\n" + "="*50)
                    print("ERROR CRÍTICO: No se encontró 'server_public.pem'")
                    print(f"Se buscó en: {ruta_pem}")
                    print("Asegúrate de ejecutar primero 'python server_main.py'")
                    print("="*50 + "\n")

        except Exception as e:
            print(f"Error al cargar la llave pública del servidor: {e}")

        # Inicializamos el cliente TCP con la llave cargada
        self.cliente_tcp = ClienteTCP(self.cola_envios, self.seguridad, llave_servidor, self.host_servidor, self.puerto_servidor)
        #mando a llamar al observador no se me olvide maldito
        self.cola_envios.agregar_observador(self.cliente_tcp)

        self.usuario_actual = None
        self.callback_mensaje = None

        # Hilo para procesar recibos (mensajes entrantes)
        threading.Thread(target=self._procesar_recepcion, daemon=True).start()

    def set_callback(self, funcion):
        self.callback_mensaje = funcion

    def registrar(self, usuario, password):
        """Envia solicitud de registro"""
        public_key_pem = self.seguridad.obtener_publica_bytes().decode('utf-8')
        
        contenido = {
            "usuario": usuario, 
            "password": password,
            "puerto_escucha": self.mi_puerto, 
            "public_key": public_key_pem      
        }
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        self.usuario_actual = usuario

        temas_susbcirpcion =[
            "CHAT_GLOBAL",
            f"MENSAJE_PRIVADO_{usuario}"
        ]
        self._enviar_paquete(
            tipo = "INICIAR_CONEXION",
            contenido=temas_susbcirpcion,
            destino="BUS"

        )

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        if destino == "TODOS":
            tipo_evento = "CHAT_GLOBAL"
        else:
            tipo_evento =  f"MENSAJE_PRIVADO_{destino}"   
        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
        }
        self._enviar_paquete(tipo_evento, contenido, destino="BUS")

    def _procesar_recepcion(self):
        """Escucha la cola de recibos y actúa"""
        while True:
            if not self.colaRecibos.esta_vacia():
                paquete = self.colaRecibos.desencolar()
                if paquete:
                    if self.callback_mensaje:
                        self.callback_mensaje(paquete)
            time.sleep(0.1)

# Instancia global
gestor_cliente = LogicaCliente()