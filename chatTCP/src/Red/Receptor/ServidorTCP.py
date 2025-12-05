"""
Servidor TCP para recepción de paquetes
Escucha conexiones entrantes y encola paquetes recibidos
Descifrado dual con respaldo automático: Híbrido (RSA+Fernet) → RSA fallback
"""
import socket
import threading
import logging
import base64
from typing import TYPE_CHECKING, Optional

from ..Cifrado.seguridad import GestorSeguridad

if TYPE_CHECKING:
    from .ColaRecibos import ColaRecibos


class ServidorTCP:
    """
    Servidor TCP que escucha conexiones entrantes y recibe paquetes JSON
    """

    def __init__(self,
                 cola: 'ColaRecibos',
                 seguridad: 'GestorSeguridad',
                 puerto: int = 5555,
                 host: str = '0.0.0.0'):
        if not seguridad:
            raise ValueError("GestorSeguridad es REQUERIDO - sin cifrado no está permitido")

        self.seguridad = seguridad
        self._cola = cola
        self._puerto = puerto
        self._host = host
        self._socket: Optional[socket.socket] = None
        self._ejecutando = False
        self._thread: Optional[threading.Thread] = None
        self._logger = logging.getLogger(__name__)

    def iniciar(self) -> None:
        if self._ejecutando:
            self._logger.warning("El servidor ya está ejecutándose")
            return

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._puerto))
            self._puerto = self._socket.getsockname()[1]
            self._socket.listen(5)
            self._ejecutando = True

            self._logger.info(f"Servidor TCP iniciado en {self._host}:{self._puerto}")

            self._thread = threading.Thread(target=self._aceptar_conexiones, daemon=True)
            self._thread.start()

        except Exception as e:
            self._logger.error(f"Error al iniciar servidor: {e}")
            self._ejecutando = False
            raise

    def detener(self) -> None:
        self._logger.info("Deteniendo servidor TCP...")
        self._ejecutando = False

        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                self._logger.error(f"Error al cerrar socket: {e}")

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

        self._logger.info("Servidor TCP detenido")

    def _aceptar_conexiones(self) -> None:
        while self._ejecutando:
            try:
                if self._socket:
                    self._socket.settimeout(1.0)
                    try:
                        cliente_socket, direccion = self._socket.accept()
                        self._logger.info(f"Conexión aceptada de {direccion}")

                        thread_cliente = threading.Thread(
                            target=self._recibir_paquete,
                            args=(cliente_socket,),
                            daemon=True
                        )
                        thread_cliente.start()

                    except socket.timeout:
                        continue

            except Exception as e:
                if self._ejecutando:
                    self._logger.error(f"Error al aceptar conexión: {e}")

    def _recibir_paquete(self, cliente_socket: socket.socket) -> None:
        try:
            buffer = []
            while True:
                chunk = cliente_socket.recv(1024).decode('utf-8')
                if not chunk:
                    break
                buffer.append(chunk)
                if '\n' in chunk:
                    break

            mensaje_recibido = ''.join(buffer).strip()

            if mensaje_recibido:
                json_str, modo_usado = self._descifrar_mensaje_dual(mensaje_recibido)

                if json_str and "Error" not in json_str:
                    self._logger.info(f"Paquete recibido [{modo_usado}]: {json_str[:50]}...")
                    self._cola.encolar(json_str)
                else:
                    self._logger.error("RECHAZO DE PAQUETE: No se pudo descifrar o formato incorrecto")
            else:
                self._logger.warning("Mensaje vacío recibido")

        except Exception as e:
            self._logger.error(f"Error al recibir paquete: {e}")
        finally:
            try:
                cliente_socket.close()
            except Exception as e:
                self._logger.error(f"Error al cerrar socket del cliente: {e}")

    def _descifrar_mensaje_dual(self, mensaje: str) -> tuple:
  
        try:
            self._logger.debug("Intentando descifrado híbrido RSA+Fernet...")
            bytes_cifrados = base64.b64decode(mensaje)
            texto_plano = self.seguridad.desifrar(bytes_cifrados)
            
            if texto_plano is None:
                raise Exception("Fallo interno en desifrar()")

            return (texto_plano, 'HIBRIDO')

        except Exception as e_hibrido:
          
            try:
                from cryptography.hazmat.primitives.asymmetric import padding
                from cryptography.hazmat.primitives import hashes

                bytes_cifrados = base64.b64decode(mensaje)
                texto_plano = self.seguridad.private_key.decrypt(
                    bytes_cifrados,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                self._logger.info("Usando RSA puro como respaldo para descifrado")
                return (texto_plano.decode('utf-8'), 'RSA')

            except Exception as e_rsa:
                
                self._logger.error(f"FALLO TOTAL DE DESCIFRADO")
                return (None, 'NINGUNO')

    def esta_ejecutando(self) -> bool:
        return self._ejecutando

    def get_puerto(self) -> int:
        return self._puerto

    def get_host(self) -> str:
        return self._host