"""
Servidor TCP para recepción de paquetes
Escucha conexiones entrantes y encola paquetes recibidos
"""
import socket
import threading
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .ColaRecibos import ColaRecibos


class ServidorTCP:
    """
    Servidor TCP que escucha conexiones entrantes y recibe paquetes JSON
    """

    def __init__(self, cola: 'ColaRecibos', puerto: int = 5555, host: str = '0.0.0.0'):
        """
        Inicializa el servidor TCP

        Args:
            cola: Cola de recibos donde se encolarán los paquetes
            puerto: Puerto donde escuchar conexiones
            host: Host donde escuchar (0.0.0.0 para todas las interfaces)
        """
        self._cola = cola
        self._puerto = puerto
        self._host = host
        self._socket: Optional[socket.socket] = None
        self._ejecutando = False
        self._thread: Optional[threading.Thread] = None
        self._logger = logging.getLogger(__name__)

    def iniciar(self) -> None:
        """
        Inicia el servidor TCP en un hilo separado
        """
        if self._ejecutando:
            self._logger.warning("El servidor ya está ejecutándose")
            return

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._puerto))
            self._socket.listen(5)
            self._ejecutando = True

            self._logger.info(f"Servidor TCP iniciado en {self._host}:{self._puerto}")

            # Iniciar thread para aceptar conexiones
            self._thread = threading.Thread(target=self._aceptar_conexiones, daemon=True)
            self._thread.start()

        except Exception as e:
            self._logger.error(f"Error al iniciar servidor: {e}")
            self._ejecutando = False
            raise

    def detener(self) -> None:
        """
        Detiene el servidor TCP
        """
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
        """
        Loop principal que acepta conexiones entrantes
        """
        while self._ejecutando:
            try:
                if self._socket:
                    self._socket.settimeout(1.0)  # Timeout para poder verificar _ejecutando
                    try:
                        cliente_socket, direccion = self._socket.accept()
                        self._logger.info(f"Conexión aceptada de {direccion}")

                        # Manejar cliente en hilo separado
                        thread_cliente = threading.Thread(
                            target=self._recibir_paquete,
                            args=(cliente_socket,),
                            daemon=True
                        )
                        thread_cliente.start()

                    except socket.timeout:
                        continue  # Timeout normal, continuar el loop

            except Exception as e:
                if self._ejecutando:
                    self._logger.error(f"Error al aceptar conexión: {e}")

    def _recibir_paquete(self, cliente_socket: socket.socket) -> None:
        """
        Recibe un paquete de un cliente y lo encola

        Args:
            cliente_socket: Socket del cliente conectado
        """
        try:
            # Configurar buffer para recibir datos
            buffer = []
            while True:
                chunk = cliente_socket.recv(1024).decode('utf-8')
                if not chunk:
                    break
                buffer.append(chunk)

                # Si encontramos newline, tenemos un mensaje completo
                if '\n' in chunk:
                    break

            # Unir todo el buffer y limpiar
            mensaje = ''.join(buffer).strip()

            if mensaje:
                self._logger.info(f"Paquete recibido: {mensaje[:100]}...")
                self._cola.encolar(mensaje)
            else:
                self._logger.warning("Mensaje vacío recibido")

        except Exception as e:
            self._logger.error(f"Error al recibir paquete: {e}")
        finally:
            try:
                cliente_socket.close()
            except Exception as e:
                self._logger.error(f"Error al cerrar socket del cliente: {e}")

    def esta_ejecutando(self) -> bool:
        """
        Verifica si el servidor está ejecutándose

        Returns:
            True si está ejecutándose, False en caso contrario
        """
        return self._ejecutando

    def get_puerto(self) -> int:
        """
        Obtiene el puerto del servidor

        Returns:
            Número de puerto
        """
        return self._puerto

    def get_host(self) -> str:
        """
        Obtiene el host del servidor

        Returns:
            Host del servidor
        """
        return self._host
