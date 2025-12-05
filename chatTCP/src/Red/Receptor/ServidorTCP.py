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

    Sistema de descifrado dual redundante (siempre cifrado, sin opción de desactivar):
    1. Intenta descifrado HÍBRIDO (RSA + Fernet) - Soporta cualquier tamaño
    2. Si falla, intenta descifrado RSA puro como RESPALDO - Solo mensajes <190 bytes
    3. NUNCA acepta mensajes sin cifrar

    Ventajas:
    - Alta seguridad por defecto
    - Tolerancia a fallos
    - Compatible con ClienteTCP dual
    - No hay opción de comunicación insegura
    """

    def __init__(self,
                 cola: 'ColaRecibos',
                 seguridad: 'GestorSeguridad',
                 puerto: int = 5555,
                 host: str = '0.0.0.0'):
        """
        Inicializa el servidor TCP con descifrado dual obligatorio

        Args:
            cola: Cola de recibos donde se encolarán los paquetes
            seguridad: Gestor de seguridad (REQUERIDO)
            puerto: Puerto donde escuchar conexiones
            host: Host donde escuchar (0.0.0.0 para todas las interfaces)

        Raises:
            ValueError: Si falta GestorSeguridad
        """
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
            self._puerto = self._socket.getsockname()[1]
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
        Descifra con sistema dual redundante

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
            mensaje_recibido = ''.join(buffer).strip()

            if mensaje_recibido:
                # Descifrar con sistema dual redundante
                json_str, modo_usado = self._descifrar_mensaje_dual(mensaje_recibido)

                if json_str:
                    self._logger.info(f"Paquete recibido [{modo_usado}]: {json_str[:50]}...")
                    self._cola.encolar(json_str)
                else:
                    self._logger.error("RECHAZO DE PAQUETE: No se pudo descifrar")
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
        """
        Descifra un mensaje con sistema dual redundante:
        1. Intenta descifrado HÍBRIDO (RSA + Fernet)
        2. Si falla, intenta descifrado RSA puro como respaldo
        3. Si ambos fallan, retorna (None, 'NINGUNO')

        Args:
            mensaje: Mensaje cifrado en base64 a descifrar

        Returns:
            tuple: (mensaje_descifrado, modo_usado) o (None, 'NINGUNO') si falla

        Proceso de descifrado híbrido (seguridad.py):
            1. Decodifica de base64 a bytes
            2. Separa por b':::'
            3. Descifra llave Fernet con RSA privada
            4. Descifra mensaje con llave Fernet
            5. Retorna JSON en texto plano
        """
        # INTENTO 1: Descifrado híbrido (preferido)
        try:
            self._logger.debug("Intentando descifrado híbrido RSA+Fernet...")
            bytes_cifrados = base64.b64decode(mensaje)

            # Proceso interno de seguridad.py:
            # - Separa: partes = bytes_cifrados.split(b':::')
            # - key_fernet_cifrada = partes[0]
            # - datos_cifrados = partes[1]
            # - Descifra llave: key_fernet = private_key.decrypt(key_fernet_cifrada)
            # - Descifra mensaje: texto_plano = Fernet(key_fernet).decrypt(datos_cifrados)
            texto_plano = self.seguridad.desifrar(bytes_cifrados)

            return (texto_plano, 'HIBRIDO')

        except Exception as e_hibrido:
            self._logger.warning(f"Descifrado híbrido falló: {e_hibrido}, intentando RSA puro...")

            # INTENTO 2: Descifrado RSA puro (respaldo)
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
                # Ambos métodos fallaron - RECHAZAR PAQUETE
                error_msg = f"RECHAZO - FALLO TOTAL DE DESCIFRADO - Híbrido: {e_hibrido}, RSA: {e_rsa}"
                self._logger.error(error_msg)
                return (None, 'NINGUNO')

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
