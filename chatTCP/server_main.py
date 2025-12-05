import sys
import os
import time
import logging

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

# loggin para la bitacora
logging.basicConfig(
    filename='servidor_bitacora.log',
    level=logging.INFO,
    format='%(asctime)s - SERVER - %(message)s'
)
# salida en la consola
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


class ReceptorLogicaServidor(IReceptor):
    def __init__(self, event_bus, ensamblador):
        self.event_bus = event_bus
        self.ensamblador = ensamblador

    @property
    def cliente_tcp(self):
        return self.ensamblador._cliente_tcp

    @property
    def seguridad(self):
        return self.ensamblador._gestor_seguridad

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        try:
            tipo = paquete.tipo
            logging.info(f"procesando el paquete pa: {tipo} de {paquete.origen}")

            if tipo == "REGISTRO":
                self._procesar_registro(paquete)
            elif tipo == "LOGIN":
                self._procesar_login(paquete)
            elif tipo == "MENSAJE":
                self._procesar_mensaje(paquete)
            elif tipo == "DESCONEXION":
                pass
        except Exception as e:
            logging.error(f"error en la logica del servidor{e}")

    def _procesar_registro(self, paquete):
        datos = paquete.contenido
        user = datos.get('usuario')
        pwd = datos.get('password')

        exito = repositorioUsuarios.guardar(user, pwd)
        tipo_resp = "REGISTRO_OK" if exito else "REGISTRO_FAIL"
        msj = "usuario creado correctamente" if exito else "este usuario ya existe"

        self._enviar_respuesta_directa(paquete.host, datos['puerto_escucha'], datos['public_key'], tipo_resp, msj)

    def _procesar_login(self, paquete):
        datos = paquete.contenido
        user = datos['usuario']

        if repositorioUsuarios.validar(user, datos['password']):
            conectados = self.event_bus.servicios_por_evento.get("MENSAJE", [])

            if len(conectados) >= 5:
                self._enviar_respuesta_directa(paquete.host, datos['puerto_escucha'], datos['public_key'], "ERROR",
                                               "Servidor Lleno")
                return
            llave_publica_user = datos['public_key'].encode('utf-8') if isinstance(datos['public_key'], str) else datos['public_key']

            nuevo_servicio = ServicioDTO(
                host=paquete.host,
                puerto=datos['puerto_escucha'],
                llave_publica=llave_publica_user
            )

            self.event_bus.registrar_servicio("MENSAJE", nuevo_servicio)
            self.event_bus.registrar_servicio("LISTA_USUARIOS", nuevo_servicio)

            logging.info(f"Usuario {user} registrado en el eventbus")

            self._enviar_respuesta_directa(paquete.host, datos['puerto_escucha'], datos['public_key'], "LOGIN_OK", user)
            self._broadcast_lista_usuarios()
        else:
            self._enviar_respuesta_directa(paquete.host, datos['puerto_escucha'], datos['public_key'], "ERROR",
                                           "Credenciales Incorrectas")

    def _procesar_mensaje(self, paquete):
        destino = paquete.destino
        subcriptores = self.event_bus.servicios_por_evento.get("MENSAJE", [])

        if destino == "TODOS":
            for servicio in subcriptores:
                if servicio.puerto == paquete.puerto_origen and servicio.host == paquete.host:
                    continue
                self._enviar_paquete_seguro(servicio, "MENSAJE", paquete.contenido, origen=paquete.origen,
                                            destino="TODOS")
        else:
            for servicio in subcriptores:
                self._enviar_paquete_seguro(servicio, "MENSAJE", paquete.contenido, origen=paquete.origen,
                                            destino=destino)

    def _broadcast_lista_usuarios(self):
        subcriptores = self.event_bus.servicios_por_evento.get("LISTA_USUARIOS", [])
        lista_nombres = ["usuarios conectados....."]
        for servicio in subcriptores:
            self._enviar_paquete_seguro(servicio, "LISTA_USUARIOS", lista_nombres, origen="SERVIDOR", destino="TODOS")

    def _enviar_respuesta_directa(self, host, puerto, public_key_pem, tipo, contenido):
        try:
            llave = self.seguridad.importar_publica(public_key_pem.encode('utf-8'))
            self.cliente_tcp.llave_destino = llave
            paquete = PaqueteDTO(tipo, contenido, origen="SERVIDOR", destino="CLIENTE", host=host,
                                 puerto_destino=puerto)
            self.ensamblador.obtener_emisor().enviar_cambio(paquete)

        except Exception as e:
            logging.error(f"Error respondiendo directo: {e}")

    def _enviar_paquete_seguro(self, servicio_dto, tipo, contenido, origen, destino):
        try:
            llave_destino_obj = self.seguridad.importar_publica(servicio_dto.llave_publica)
            self.cliente_tcp.llave_destino = llave_destino_obj

            paquete = PaqueteDTO(
                tipo=tipo,
                contenido=contenido,
                origen=origen,
                destino=destino,
                host=servicio_dto.host,
                puerto_destino=servicio_dto.puerto
            )
            self.ensamblador.obtener_emisor().enviar_cambio(paquete)
        except Exception as e:
            logging.error(f"Error enviando paquete seguro: {e}")


class ServidorBusApp:
    def iniciar(self):
        print("=== SERVIDOR EVENT BUS INICIADO (Puerto 5000) ===")

        self.ensamblador = EnsambladorRed.obtener_instancia()
        self.event_bus = EventBus()
        self.seguridad = GestorSeguridad()

        self.ensamblador._gestor_seguridad = self.seguridad

        # 2. Guardar llave pública del servidor (Handshake inicial)
        with open("server_public.pem", "wb") as f:
            f.write(self.seguridad.obtener_publica_bytes())

        # 3. Configuración de Red
        # Usamos nuestra propia llave como placeholder inicial para el emisor
        config = ConfigRed(
            host_escucha="0.0.0.0",
            puerto_escucha=5000,
            host_destino="localhost",
            puerto_destino=5000,
            llave_publica_destino=self.seguridad.public_key
        )

        # 4. Crear el Receptor Lógico (Controlador) e inyectar dependencias
        self.receptor_logica = ReceptorLogicaServidor(self.event_bus, self.ensamblador)

        # 5. Ensamblar todo (Red -> ReceptorLogica)
        self.ensamblador.ensamblar(self.receptor_logica, config)

        # 6. Inyectar el emisor al EventBus (para que el bus tenga referencia, aunque usemos la lógica manual)
        self.event_bus.set_emisor(self.ensamblador.obtener_emisor())
        self.event_bus.set_llave_publica_propia(self.seguridad.obtener_publica_bytes())

        # Bucle de vida
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo servidor...")
            self.ensamblador.detener()


if __name__ == "__main__":
    app = ServidorBusApp()
    app.iniciar()
