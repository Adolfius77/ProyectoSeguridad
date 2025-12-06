import sys
import os
import time
import logging

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(current_dir)
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
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - SERVER - %(message)s')
logging.getLogger('').addHandler(logging.StreamHandler())

class ReceptorLogicaServidor(IReceptor):
    def __init__(self, event_bus, ensamblador):
        self.event_bus = event_bus
        self.ensamblador = ensamblador
        self.usuarios_conectados  = {}

    @property
    def cliente_tcp(self):
        return self.ensamblador._cliente_tcp

    @property
    def seguridad(self):
        return self.ensamblador._gestor_seguridad

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        try:
            tipo = paquete.tipo
            logging.info(f"Procesando paquete: {tipo} de {paquete.origen}")

            if tipo == "REGISTRO": self._procesar_registro(paquete)
            elif tipo == "LOGIN": self._procesar_login(paquete)
            elif tipo == "MENSAJE": self._procesar_mensaje(paquete)
            elif tipo == "SOLICITAR_USUARIOS": self._broadcast_lista_usuarios()

        except Exception as e:
            logging.error(f"Error en logica servidor: {e}")

    def _procesar_registro(self, paquete):
        datos = paquete.contenido
        user = datos.get('usuario')
        host_respuesta = datos.get('host_escucha', paquete.host)

        exito = repositorioUsuarios.guardar(user, datos.get('password'))
        tipo_resp = "REGISTRO_OK" if exito else "REGISTRO_FAIL"
        msj = "Usuario creado correctamente" if exito else "El usuario ya existe"

        logging.info(f"Registro {user}: {tipo_resp}")
        self._enviar_respuesta_directa(host_respuesta, datos['puerto_escucha'], datos['public_key'], tipo_resp, msj)

    def _procesar_login(self, paquete):
        datos = paquete.contenido
        user = datos['usuario']
        host_respuesta = datos.get('host_escucha', paquete.host)
        
        logging.info(f"Login {user} desde {host_respuesta}:{datos['puerto_escucha']}")

        if repositorioUsuarios.validar(user, datos['password']):
            llave = datos['public_key'].encode('utf-8') if isinstance(datos['public_key'], str) else datos['public_key']
            nuevo_servicio = ServicioDTO(host=host_respuesta, puerto=datos['puerto_escucha'], llave_publica=llave)
            
            # Limpiar sesión anterior
            if user in self.usuarios_conectados:
                old = self.usuarios_conectados[user]
                self.event_bus.eliminar_servicio("MENSAJE", old)
                self.event_bus.eliminar_servicio("LISTA_USUARIOS", old)
            
            self.usuarios_conectados[user] = nuevo_servicio
            self.event_bus.registrar_servicio("MENSAJE", nuevo_servicio)
            self.event_bus.registrar_servicio("LISTA_USUARIOS", nuevo_servicio)

            self._enviar_respuesta_directa(host_respuesta, datos['puerto_escucha'], datos['public_key'], "LOGIN_OK", user)
            time.sleep(0.2)
            self._broadcast_lista_usuarios()
        else:
            self._enviar_respuesta_directa(host_respuesta, datos['puerto_escucha'], datos['public_key'], "ERROR", "Credenciales Incorrectas")

    def _procesar_mensaje(self, paquete):
        destino = paquete.destino
        subs = self.event_bus.servicios_por_evento.get("MENSAJE", [])

        if destino == "TODOS":
            for s in subs:
                if s.puerto == paquete.puerto_origen and s.host == paquete.host: continue
                self._enviar_paquete_seguro(s, "MENSAJE", paquete.contenido, origen=paquete.origen, destino="TODOS")
        else:
            dest_serv = self.usuarios_conectados.get(destino)
            if dest_serv:
                self._enviar_paquete_seguro(dest_serv, "MENSAJE", paquete.contenido, origen=paquete.origen, destino=destino)

    def _broadcast_lista_usuarios(self):
        subs = self.event_bus.servicios_por_evento.get("LISTA_USUARIOS", [])
        nombres = list(self.usuarios_conectados.keys())
        for s in subs:
            self._enviar_paquete_seguro(s, "LISTA_USUARIOS", nombres, origen="SERVIDOR", destino="TODOS")

    def _enviar_respuesta_directa(self, host, puerto, public_key_pem, tipo, contenido):
        try:
            llave = self.seguridad.importar_publica(public_key_pem.encode('utf-8'))
            self.cliente_tcp.llave_destino = llave
            paquete = PaqueteDTO(tipo, contenido, origen="SERVIDOR", destino="CLIENTE", host=host, puerto_destino=puerto)
            self.ensamblador.obtener_emisor().enviar_cambio(paquete)
        except Exception as e:
            logging.error(f"Error respondiendo directo: {e}")

    def _enviar_paquete_seguro(self, servicio, tipo, contenido, origen, destino):
        try:
            llave = self.seguridad.importar_publica(servicio.llave_publica)
            self.cliente_tcp.llave_destino = llave
            paquete = PaqueteDTO(tipo, contenido, origen=origen, destino=destino, host=servicio.host, puerto_destino=servicio.puerto)
            self.ensamblador.obtener_emisor().enviar_cambio(paquete)
        except Exception as e:
            logging.error(f"Error enviando seguro: {e}")

class ServidorBusApp:
    def iniciar(self):
        print("=== SERVIDOR INICIADO ===")
        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.event_bus = EventBus()
        self.seguridad = GestorSeguridad()
        
        with open(os.path.join(current_dir, "server_public.pem"), "wb") as f:
            f.write(self.seguridad.obtener_publica_bytes())

        self.ensamblador._gestor_seguridad = self.seguridad
        config = ConfigRed(host_escucha="0.0.0.0", puerto_escucha=5555, host_destino="localhost", puerto_destino=5555, llave_publica_destino=self.seguridad.public_key)

        self.receptor = ReceptorLogicaServidor(self.event_bus, self.ensamblador)
        self.ensamblador.ensamblar(self.receptor, config)
        self.event_bus.set_emisor(self.ensamblador.obtener_emisor())
        self.event_bus.set_llave_publica_propia(self.seguridad.obtener_publica_bytes())

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            self.ensamblador.detener()

if __name__ == "__main__":
    app = ServidorBusApp()
    app.iniciar()