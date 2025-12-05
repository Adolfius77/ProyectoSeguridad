import threading
import time
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
chat_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.insert(0, chat_root)

from src.PaqueteDTO.PaqueteDTO import PaqueteDTO
from src.Red.EnsambladorRed import EnsambladorRed, ConfigRed
from src.ComponenteReceptor.IReceptor import IReceptor
from src.Red.Cifrado.seguridad import GestorSeguridad


class ReceptorCliente(IReceptor):
    """
    Adaptador que recibe eventos de la red (via Ensamblador)
    y los pasa a la Interfaz Gráfica.
    Cumple la función que tendría el PublicadorEventos en el lado del servidor/bus.
    """

    def __init__(self):
        self.callback = None

    def set_callback(self, funcion):
        self.callback = funcion

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        """Método de la interfaz IReceptor llamado por la capa de Red"""
        if self.callback:
            try:

                self.callback(paquete)
            except Exception as e:
                print(f"[ReceptorCliente] Error en callback de UI: {e}")
        else:
            print(f"[ReceptorCliente] Paquete recibido sin callback configurado: {paquete.tipo}")


class LogicaCliente:
    def __init__(self):
        # 1. Obtener la instancia Singleton del Ensamblador
        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.gestor_seguridad = GestorSeguridad()  # Usamos gestor auxiliar para cargar llave pem

        # 2. Configurar puertos y hosts
        self.host_servidor = "localhost"
        self.puerto_servidor = 5000

        # 3. Cargar llave pública del servidor (Indispensable para ConfigRed)
        llave_servidor = self._cargar_llave_servidor()

        # 4. Configurar la Red usando la clase ConfigRed
        # Puerto escucha 0 = puerto aleatorio dinámico
        config = ConfigRed(
            host_escucha="0.0.0.0",
            puerto_escucha=0,
            host_destino=self.host_servidor,
            puerto_destino=self.puerto_servidor,
            llave_publica_destino=llave_servidor
        )

        # 5. Instanciar nuestro adaptador de recepción
        self.receptor_interno = ReceptorCliente()

        try:
            print("[LogicaCliente] Ensamblando red con arquitectura...")
            self.emisor = self.ensamblador.ensamblar(self.receptor_interno, config)

            time.sleep(0.5)

            if self.ensamblador._servidor:
                self.mi_puerto = self.ensamblador._servidor.get_puerto()
                print(f"[LogicaCliente] Red ensamblada. Escuchando en puerto: {self.mi_puerto}")
            else:
                raise Exception("El servidor interno no se inició correctamente")

        except Exception as e:
            print(f"[LogicaCliente] ERROR CRÍTICO al ensamblar red: {e}")
            self.emisor = None
            self.mi_puerto = 0

        self.usuario_actual = None

    def set_callback(self, funcion):
        """Conecta la UI con el receptor interno"""
        print(f"[LogicaCliente] Conectando UI al Receptor de Red")
        self.receptor_interno.set_callback(funcion)

    def registrar(self, usuario, password):
        """Envia solicitud de registro"""
        if not self._validar_conexion(): return

        # Obtenemos nuestra llave pública del ensamblador
        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem
        }
        self._enviar_paquete("REGISTRO", contenido)

    def login(self, usuario, password):
        """Envia solicitud de login"""
        if not self._validar_conexion(): return

        self.usuario_actual = usuario
        public_key_pem = self.ensamblador.obtener_llave_publica().decode('utf-8')

        contenido = {
            "usuario": usuario,
            "password": password,
            "puerto_escucha": self.mi_puerto,
            "public_key": public_key_pem,
        }
        self._enviar_paquete("LOGIN", contenido)

    def enviar_mensaje(self, mensaje, destino="TODOS"):
        """Envia un mensaje de chat"""
        if not self._validar_conexion(): return

        contenido = {
            "mensaje": mensaje,
            "remitente": self.usuario_actual
        }
        self._enviar_paquete("MENSAJE", contenido, destino=destino)

    def _enviar_paquete(self, tipo, contenido, destino="SERVIDOR"):
        paquete = PaqueteDTO(
            tipo=tipo,
            contenido=contenido,
            origen=self.usuario_actual if self.usuario_actual else "ANONIMO",
            destino=destino,
            host=self.host_servidor,
            puerto_destino=self.puerto_servidor
        )
        # Usamos la interfaz IEmisor proporcionada por el ensamblador
        self.emisor.enviar_cambio(paquete)

    def _validar_conexion(self):
        if self.emisor is None:
            print("[ERROR] Red no ensamblada correctamente.")
            return False
        return True

    def _cargar_llave_servidor(self):
        """Lógica auxiliar para encontrar el .pem del servidor"""
        rutas = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "server_public.pem"),
            "server_public.pem"
        ]

        for ruta in rutas:
            ruta_abs = os.path.abspath(ruta)
            if os.path.exists(ruta_abs):
                try:
                    with open(ruta_abs, "rb") as f:
                        print(f"[LogicaCliente] Llave servidor cargada de: {ruta_abs}")
                        return self.gestor_seguridad.importar_publica(f.read())
                except Exception as e:
                    print(f"[LogicaCliente] Error leyendo llave: {e}")

        print("[LogicaCliente] ADVERTENCIA: No se encontró 'server_public.pem'. La conexión fallará.")
        return None
    #Ya quedo el metodo jack para que lo uses pa
    def obtener_usuarios(self):
        if not self._validar_conexion(): return
        print("solicitando lista de usuarios al servidor...")
        self._enviar_paquete("SOLICITAR_USUARIOS", {})

# Instancia global
gestor_cliente = LogicaCliente()
