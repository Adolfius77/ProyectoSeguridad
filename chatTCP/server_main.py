import time
import logging
from src.Red.Receptor.ServidorTCP import ServidorTCP
from src.Red.Receptor.ColaRecibos import ColaRecibos
from src.Red.Emisor.ClienteTCP import ClienteTCP
from src.Red.Emisor.ColaEnvios import ColaEnvios
from src.Red.Cifrado.seguridad import GestorSeguridad
from src.Datos.repositorio import repositorioUsuarios
from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

# Configuración Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SERVER - %(message)s')


class ServidorCentral:
    def __init__(self):
        self.cola_recibos = ColaRecibos()
        self.cola_envios = ColaEnvios()
        self.seguridad = GestorSeguridad()

        with open("server_public.pem", "wb") as f:
            f.write(self.seguridad.obtener_publica_bytes())
        print("llave publica guardada en 'server_public.pem'")

        # Mapa de usuarios conectados
        self.usuarios_conectados = {}

        # Servidor escuchando en puerto 5000
        self.servidor = ServidorTCP(self.cola_recibos, self.seguridad, puerto=5000, host="0.0.0.0")

        # Emisor auxiliar
        self.emisor = ClienteTCP(self.cola_envios, self.seguridad, None)

    def iniciar(self):
        print("=== Servidor de Chat Iniciado en puerto 5000 ===")
        self.servidor.iniciar()

        while True:
            if not self.cola_recibos.esta_vacia():
                paquete = self.cola_recibos.desencolar()
                if paquete:
                    self.procesar_paquete(paquete)
            time.sleep(0.01)

    def procesar_paquete(self, paquete):
        try:
            tipo = paquete.tipo
            contenido = paquete.contenido

            if tipo == "REGISTRO":
                exito = repositorioUsuarios.guardar(contenido['usuario'], contenido['password'])
                respuesta = "REGISTRO_OK" if exito else "REGISTRO_FAIL"
                logging.info(f"Registro {contenido['usuario']}: {respuesta}")
                
               
                puerto_cliente = contenido.get('puerto_escucha')
                public_key_pem = contenido.get('public_key')
                
                if puerto_cliente and public_key_pem:
                    # Enviamos la respuesta de vuelta
                    self._responder(paquete.host, puerto_cliente, respuesta, "Resultado Registro", public_key_pem)

            elif tipo == "LOGIN":
                user = contenido['usuario']
                pwd = contenido['password']
                puerto_cliente = contenido.get('puerto_escucha')
                public_key_pem = contenido.get('public_key')

                # Validar credenciales
                if repositorioUsuarios.validar(user, pwd):
                    if len(self.usuarios_conectados) >= 5:
                        self._responder(paquete.host, puerto_cliente, "ERROR", "Servidor lleno", public_key_pem)
                        return

                    # Registrar usuario conectado
                    self.usuarios_conectados[user] = {
                        "host": paquete.host,  # IP desde donde viene
                        "puerto": puerto_cliente,
                        "key": self.seguridad.importar_publica(public_key_pem.encode('utf-8'))
                    }

                    logging.info(f"Usuario {user} logueado desde {paquete.host}:{puerto_cliente}")

                    # Confirmar Login
                    self._responder(paquete.host, puerto_cliente, "LOGIN_OK", "Bienvenido", public_key_pem)

                    # Broadcast nueva lista de usuarios
                    self._broadcast_usuarios()
                else:
                    logging.warning(f"Login fallido para {user}")

            elif tipo == "MENSAJE":
                destino = paquete.destino
                origen = paquete.origen

                if destino == "TODOS":
                    # Broadcast a todos menos al que envio
                    for u, datos in self.usuarios_conectados.items():
                        if u != origen:
                            self._enviar_paquete(datos, "MENSAJE", contenido)
                elif destino in self.usuarios_conectados:
                    # Mensaje Privado
                    datos = self.usuarios_conectados[destino]
                    self._enviar_paquete(datos, "MENSAJE", contenido)

        except Exception as e:
            logging.error(f"Error procesando paquete: {e}")

    def _responder(self, host, puerto, tipo, mensaje, public_key_pem):
        """Responde directamente a un cliente temporal"""

        key_obj = self.seguridad.importar_publica(public_key_pem.encode('utf-8'))

        paquete = PaqueteDTO(tipo, mensaje, origen="SERVIDOR", destino="CLIENTE", host=host, puerto_destino=puerto)

        # Configuramos el emisor temporalmente
        self.emisor.llave_destino = key_obj
        self.emisor._enviar_paquete(paquete.to_json(), host, puerto)

    def _broadcast_usuarios(self):
        lista = list(self.usuarios_conectados.keys())
        contenido = lista

        for u, datos in self.usuarios_conectados.items():
            self._enviar_paquete(datos, "LISTA_USUARIOS", contenido)

    def _enviar_paquete(self, datos_usuario, tipo, contenido):
        host = datos_usuario['host']
        puerto = datos_usuario['puerto']
        llave = datos_usuario['key']

        paquete = PaqueteDTO(tipo, contenido, origen="SERVIDOR", destino=host)  # Host destino

        self.emisor.llave_destino = llave
        self.emisor._enviar_paquete(paquete.to_json(), host, puerto)


if __name__ == "__main__":
    server = ServidorCentral()
    server.iniciar()
