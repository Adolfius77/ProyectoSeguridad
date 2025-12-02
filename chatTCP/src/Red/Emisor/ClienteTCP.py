"""
Cliente TCP para envío de paquetes
Implementa patrón Observer
"""
import base64
import socket
import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ColaEnvios import ColaEnvios

from ..ObserverEmisor.ObservadorEnvios import ObservadorEnvios
from ...Red.Cifrado.seguridad import GestorSeguridad


class ClienteTCP(ObservadorEnvios):
    """
    Cliente TCP que envía paquetes cuando es notificado por la cola de envíos
    """

    def __init__(self, cola: 'ColaEnvios', seguridad: 'GestorSeguridad', llave_destino, host: str = 'localhost',
                 puerto: int = 5555):
        """
        Inicializa el cliente TCP

        Args:
            cola: Cola de envíos a observar
            host: Host por defecto para conexiones
            puerto: Puerto por defecto para conexiones
        """
        self._cola = cola
        self.seguridad = seguridad
        self.llave_destino = llave_destino
        self._host = host
        self._puerto = puerto
        self._logger = logging.getLogger(__name__)

    def actualizar(self) -> None:
        """
        Método llamado cuando hay paquetes disponibles en la cola
        Desencola y envía el paquete
        """
        json_str = self._cola.desencolar()
        if json_str:
            try:
                # Parsear JSON para obtener información de destino
                data = json.loads(json_str)
                host = data.get('host', self._host)
                puerto = data.get('puerto_destino', self._puerto)

                self._logger.info(f"Enviando paquete a {host}:{puerto}")
                self._enviar_paquete(json_str, host, puerto)
            except json.JSONDecodeError as e:
                self._logger.error(f"Error al parsear JSON: {e}")
            except Exception as e:
                self._logger.error(f"Error al enviar paquete: {e}")

    def _enviar_paquete(self, json_str: str, host: str, puerto: int) -> None:
        """
        Envía un paquete JSON por TCP

        Args:
            json_str: String JSON a enviar
            host: Host destino
            puerto: Puerto destino
        """
        try:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5.0)  # Timeout de 5 segundos
                sock.connect((host, puerto))

                # cifrar el json este devuelve bytes
                bytes_cifrados = self.seguridad.cifrar(json_str, self.llave_destino)

                # convertir a base 64 para evitar que viaje como texto seguro sin romper el protocolo
                mesanje_64 = base64.b64encode(bytes_cifrados).decode('utf-8')

                # agrega el salto de linea
                mensaje_final = mesanje_64 + '\n'

                # Enviar el paquete (agregar newline para delimitación)

                sock.sendall(mensaje_final.encode('utf-8'))

                self._logger.info(f"Paquete enviado exitosamente a {host}:{puerto}")
        except socket.timeout:
            self._logger.error(f"Timeout al conectar a {host}:{puerto}")
            raise
        except ConnectionRefusedError:
            self._logger.error(f"Conexión rechazada por {host}:{puerto}")
            raise
        except Exception as e:
            self._logger.error(f"Error al enviar paquete a {host}:{puerto}: {e}")
            raise

    def set_host_puerto(self, host: str, puerto: int) -> None:
        """
        Establece el host y puerto por defecto

        Args:
            host: Nuevo host
            puerto: Nuevo puerto
        """
        self._host = host
        self._puerto = puerto
        self._logger.info(f"Host y puerto actualizados: {host}:{puerto}")
