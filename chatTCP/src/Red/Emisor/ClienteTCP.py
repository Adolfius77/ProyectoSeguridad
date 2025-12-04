"""
Cliente TCP para envío de paquetes
Implementa patrón Observer
Cifrado dual con respaldo automático: Híbrido (RSA+Fernet) → RSA fallback
"""
import base64
import socket
import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ColaEnvios import ColaEnvios

from ..ObserverEmisor.ObservadorEnvios import ObservadorEnvios
from ..Cifrado.seguridad import GestorSeguridad


class ClienteTCP(ObservadorEnvios):
    """
    Cliente TCP que envía paquetes cuando es notificado por la cola de envíos

    Sistema de cifrado dual redundante (siempre cifrado, sin opción de desactivar):
    1. Intenta cifrado HÍBRIDO (RSA + Fernet) - Soporta cualquier tamaño
    2. Si falla, usa cifrado RSA puro como RESPALDO - Solo mensajes <190 bytes
    3. NUNCA envía mensajes sin cifrar

    Ventajas:
    - Alta seguridad por defecto
    - Tolerancia a fallos
    - No hay opción de comunicación insegura
    """

    def __init__(self,
                 cola: 'ColaEnvios',
                 seguridad: 'GestorSeguridad',
                 llave_destino,
                 host: str = 'localhost',
                 puerto: int = 5555):
        """
        Inicializa el cliente TCP con cifrado dual obligatorio

        Args:
            cola: Cola de envíos a observar
            seguridad: Gestor de seguridad (REQUERIDO)
            llave_destino: Llave pública del destino (REQUERIDA)
            host: Host por defecto para conexiones
            puerto: Puerto por defecto para conexiones

        Raises:
            ValueError: Si falta seguridad o llave_destino
        """
        if not seguridad:
            raise ValueError("GestorSeguridad es REQUERIDO - sin cifrado no está permitido")
        if not llave_destino:
            raise ValueError("Llave pública del destino es REQUERIDA")

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
        Envía un paquete JSON por TCP con cifrado dual redundante

        Args:
            json_str: String JSON a enviar
            host: Host destino
            puerto: Puerto destino

        Raises:
            Exception: Si falla tanto cifrado híbrido como RSA
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5.0)  # Timeout de 5 segundos
                sock.connect((host, puerto))

                # Cifrar con sistema dual redundante
                mensaje_final, modo_usado = self._cifrar_mensaje_dual(json_str)

                # Enviar el paquete
                sock.sendall(mensaje_final.encode('utf-8'))

                self._logger.info(f"Paquete enviado [{modo_usado}] a {host}:{puerto}")
        except socket.timeout:
            self._logger.error(f"Timeout al conectar a {host}:{puerto}")
            raise
        except ConnectionRefusedError:
            self._logger.error(f"Conexión rechazada por {host}:{puerto}")
            raise
        except Exception as e:
            self._logger.error(f"Error al enviar paquete a {host}:{puerto}: {e}")
            raise

    def _cifrar_mensaje_dual(self, json_str: str) -> tuple:
        """
        Cifra un mensaje con sistema dual redundante:
        1. Intenta cifrado HÍBRIDO (RSA + Fernet)
        2. Si falla, usa cifrado RSA puro como respaldo
        3. Si ambos fallan, lanza excepción

        Args:
            json_str: Mensaje JSON a cifrar

        Returns:
            tuple: (mensaje_cifrado_con_newline, modo_usado)

        Raises:
            Exception: Si fallan ambos métodos de cifrado

        Proceso de cifrado híbrido (seguridad.py):
            1. Genera llave Fernet efímera
            2. Cifra mensaje con Fernet (soporta cualquier tamaño)
            3. Cifra llave Fernet con RSA-OAEP
            4. Concatena: key_fernet_cifrada + b':::' + datos_cifrados
            5. Codifica en base64
        """
        # INTENTO 1: Cifrado híbrido (preferido)
        try:
            self._logger.debug("Intentando cifrado híbrido RSA+Fernet...")
            bytes_cifrados = self.seguridad.cifrar(json_str, self.llave_destino)
            mensaje_b64 = base64.b64encode(bytes_cifrados).decode('utf-8')
            return (mensaje_b64 + '\n', 'HIBRIDO')

        except Exception as e_hibrido:
            self._logger.warning(f"Cifrado híbrido falló: {e_hibrido}, intentando RSA puro...")

            # INTENTO 2: Cifrado RSA puro (respaldo)
            try:
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes

                # Verificar tamaño del mensaje
                if len(json_str.encode('utf-8')) > 190:
                    raise ValueError(f"Mensaje muy grande para RSA puro ({len(json_str)} bytes > 190)")

                bytes_cifrados = self.llave_destino.encrypt(
                    json_str.encode('utf-8'),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                mensaje_b64 = base64.b64encode(bytes_cifrados).decode('utf-8')
                self._logger.info("Usando RSA puro como respaldo")
                return (mensaje_b64 + '\n', 'RSA')

            except Exception as e_rsa:
                # Ambos métodos fallaron
                error_msg = f"FALLO TOTAL DE CIFRADO - Híbrido: {e_hibrido}, RSA: {e_rsa}"
                self._logger.error(error_msg)
                raise Exception(error_msg)

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
