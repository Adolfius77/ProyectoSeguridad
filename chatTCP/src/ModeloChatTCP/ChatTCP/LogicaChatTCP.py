"""
Clase que maneja la lógica del ChatTCP para enviar y recibir mensajes.
Tiene como parámetros un IEmisor y el UsuarioDTO en sesión.
"""
import logging
from typing import Optional, List
from chatTCP.src.ComponenteEmisor.IEmisor import IEmisor
from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO
from chatTCP.src.ModeloChatTCP.DTOs.MensajeDTO import MensajeDTO
from chatTCP.src.ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO
from chatTCP.src.ModeloChatTCP.Entidades.TipoEventos import TiposEvento
from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuarioOP


class LogicaChatTCP:
    """
    Lógica central del Chat TCP que coordina el envío de mensajes.
    Trabaja con el EventBus para publicar eventos.
    """

    def __init__(self, usuarioDTO: UsuarioDTO, emisor: IEmisor, modelo_chat_tcp=None, host_eventbus: str = None, puerto_eventbus: int = None):
        """
        Inicializa la lógica del chat.

        Args:
            usuarioDTO: Usuario actual en sesión
            emisor: Componente emisor para enviar paquetes
            modelo_chat_tcp: Referencia a ModeloChatTCP para notificaciones (opcional)
            host_eventbus: Host del EventBus (opcional)
            puerto_eventbus: Puerto del EventBus (opcional)
        """
        self.usuarioEnSesion = usuarioDTO
        self.emisor = emisor
        self._logger = logging.getLogger(__name__)

        # Referencia a ModeloChatTCP para notificar cuando se reciban mensajes
        self._modelo_chat_tcp = modelo_chat_tcp

        # Configuración del EventBus
        self._host_eventbus = host_eventbus
        self._puerto_eventbus = puerto_eventbus

    # ==================== CONFIGURACIÓN ====================

    def set_modelo_chat_tcp(self, modelo_chat_tcp) -> None:
        """
        Configura la referencia a ModeloChatTCP para notificaciones.

        Args:
            modelo_chat_tcp: Instancia de ModeloChatTCP
        """
        self._modelo_chat_tcp = modelo_chat_tcp
        self._logger.info("ModeloChatTCP configurado en LogicaChatTCP")

    def set_eventbus(self, host_eventbus: str, puerto_eventbus: int) -> None:
        """
        Configura el host y puerto del EventBus.

        Args:
            host_eventbus: Host del EventBus
            puerto_eventbus: Puerto del EventBus
        """
        self._host_eventbus = host_eventbus
        self._puerto_eventbus = puerto_eventbus
        self._logger.info(f"EventBus configurado: {host_eventbus}:{puerto_eventbus}")

    # ==================== ENVÍO DE MENSAJES ====================

    def enviarMensajePrivado(self, usuarioDestino: UsuarioOP, contenidoMensaje: str) -> None:
        """
        Crea un MensajeDTO y lo envía como PaqueteDTO al EventBus para que lo distribuya.

        Args:
            usuarioDestino: Usuario destino del mensaje
            contenidoMensaje: Contenido del mensaje a enviar
        """
        self._logger.info(f"Enviando mensaje privado a {usuarioDestino.nombre}: {contenidoMensaje}")

        # Crear el MensajeDTO
        mensajeDTO = MensajeDTO(
            nombreUsuario=self.usuarioEnSesion.nombre_usuario,
            contenidoMensaje=contenidoMensaje,
            usuarioDestino=usuarioDestino,
            usuarioOrigen=self.usuarioEnSesion
        )

        # Crear paquete con tipo de evento MENSAJE_PRIVADO y enviarlo al EventBus
        paqueteDTO = PaqueteDTO(
            tipo=TiposEvento.mensajePrivado.value,
            contenido=mensajeDTO.to_dict(),
            origen=self.usuarioEnSesion.nombre_usuario,
            destino=usuarioDestino.nombre,
            host=self._host_eventbus,  # Enviar al EventBus
            puerto_origen=self.usuarioEnSesion.puerto,
            puerto_destino=self._puerto_eventbus,  # Puerto del EventBus
            llave_publica_origen=self.usuarioEnSesion.public_key.encode(
                'utf-8') if self.usuarioEnSesion.public_key else None
        )

        # Enviar el paquete
        self.emisor.enviar_cambio(paqueteDTO)

    def enviarMensajeGrupal(self, contenidoMensaje: str) -> None:
        """
        Envía un mensaje grupal (broadcast) al EventBus para que lo distribuya a todos los usuarios conectados.

        Args:
            contenidoMensaje: Contenido del mensaje a enviar
        """
        self._logger.info(f"Enviando mensaje grupal: {contenidoMensaje}")

        # Crear el MensajeDTO sin usuario destino específico
        mensajeDTO = MensajeDTO(
            nombreUsuario=self.usuarioEnSesion.nombre_usuario,
            contenidoMensaje=contenidoMensaje,
            usuarioOrigen=self.usuarioEnSesion
        )

        # Crear paquete con tipo de evento MENSAJE_GRUPAL y enviarlo al EventBus
        paqueteDTO = PaqueteDTO(
            tipo=TiposEvento.mensajeGrupal.value,
            contenido=mensajeDTO.to_dict(),
            origen=self.usuarioEnSesion.nombre_usuario,
            destino="TODOS",  # Broadcast
            host=self._host_eventbus,  # Enviar al EventBus
            puerto_origen=self.usuarioEnSesion.puerto,
            puerto_destino=self._puerto_eventbus,  # Puerto del EventBus
            llave_publica_origen=self.usuarioEnSesion.public_key.encode(
                'utf-8') if self.usuarioEnSesion.public_key else None
        )

        # Enviar el paquete
        self.emisor.enviar_cambio(paqueteDTO)

    def registrarseEnEventBus(self, host_bus: str, puerto_bus: int) -> None:
        """
        Registra este usuario en el EventBus para escuchar eventos específicos.
        Envía evento INICIAR_CONEXION al bus.
        Se suscribe a los eventos: UNIRSE_GRUPAL, MENSAJE_PRIVADO, MENSAJE_GRUPAL

        Args:
            host_bus: Host del EventBus
            puerto_bus: Puerto del EventBus
        """
        eventos = [
            TiposEvento.unirseGrupal.value,
            TiposEvento.mensajePrivado.value,
            TiposEvento.mensajeGrupal.value
        ]

        self._logger.info(f"Registrándose en EventBus para eventos: {eventos}")

        paqueteDTO = PaqueteDTO(
            tipo=TiposEvento.iniciarConexion.value,
            contenido=eventos,  # Lista de eventos específicos a suscribirse
            origen=self.usuarioEnSesion.nombre_usuario,
            destino="EVENTBUS",
            host=host_bus,
            puerto_origen=self.usuarioEnSesion.puerto,
            puerto_destino=puerto_bus,
            llave_publica_origen=self.usuarioEnSesion.public_key.encode(
                'utf-8') if self.usuarioEnSesion.public_key else None
        )

        self.emisor.enviar_cambio(paqueteDTO)

    def desconectar(self) -> None:
        """Envía notificación de desconexión al EventBus"""
        self._logger.info(f"Desconectando usuario: {self.usuarioEnSesion.nombre_usuario}")

        paqueteDTO = PaqueteDTO(
            tipo=TiposEvento.DESCONEXION,
            contenido={"usuario": self.usuarioEnSesion.nombre_usuario},
            origen=self.usuarioEnSesion.nombre_usuario,
            destino="SERVIDOR",
            puerto_origen=self.usuarioEnSesion.puerto,
            llave_publica_origen=self.usuarioEnSesion.public_key.encode(
                'utf-8') if self.usuarioEnSesion.public_key else None
        )

        self.emisor.enviar_cambio(paqueteDTO)

    # ==================== PROCESAMIENTO DE EVENTOS RECIBIDOS ====================

    def procesarEvento(self, paquete: PaqueteDTO) -> None:
        """
        Procesa un paquete recibido del EventBus.
        Este método debe ser llamado por el ReceptorMensaje.

        Args:
            paquete: Paquete recibido
        """
        try:
            tipo = paquete.tipo
            self._logger.info(f"Procesando evento tipo: {tipo}")

            if tipo == TiposEvento.mensajePrivado.value:
                self._procesarMensajePrivado(paquete)

            elif tipo == TiposEvento.mensajeGrupal.value:
                self._procesarMensajeGrupal(paquete)

            else:
                self._logger.warning(f"Tipo de evento no reconocido: {tipo}")

        except Exception as e:
            self._logger.error(f"Error procesando evento {paquete.tipo}: {e}")

    def _procesarMensajePrivado(self, paquete: PaqueteDTO) -> None:
        """Procesa un mensaje privado recibido"""
        contenido = paquete.contenido

        if isinstance(contenido, dict):
            # Si el contenido es un diccionario con estructura de MensajeDTO
            mensaje_dto = MensajeDTO(
                nombreUsuario=contenido.get("nombreUsuario", paquete.origen),
                contenidoMensaje=contenido.get("contenidoMensaje", str(contenido))
            )
        else:
            # Si el contenido es texto plano
            mensaje_dto = MensajeDTO(
                nombreUsuario=paquete.origen,
                contenidoMensaje=str(contenido)
            )

        self._logger.info(f"Mensaje privado recibido de {mensaje_dto.nombreUsuario}: {mensaje_dto.contenidoMensaje}")

        # Notificar a ModeloChatTCP que a su vez notifica a los observadores
        if self._modelo_chat_tcp:
            # Convertir MensajeDTO a UsuarioOP
            usuario_op = UsuarioOP(
                nombre=mensaje_dto.nombreUsuario,
                ip="",  # No necesario para notificación
                puerto=0,  # No necesario para notificación
                ultimo_mensaje=mensaje_dto.contenidoMensaje
            )

            # Notificar a través de ModeloChatTCP
            self._modelo_chat_tcp.notificar(usuario_op)

    # ==================== GETTERS ====================

    def obtenerUsuarioActual(self) -> UsuarioDTO:
        """Retorna el usuario actualmente en sesión"""
        return self.usuarioEnSesion

    def _procesarMensajeGrupal(self, paquete: PaqueteDTO) -> None:
        """Procesa un mensaje grupal recibido"""
        contenido = paquete.contenido

        if isinstance(contenido, dict):
            # Si el contenido es un diccionario con estructura de MensajeDTO
            mensaje_dto = MensajeDTO(
                nombreUsuario=contenido.get("nombreUsuario", paquete.origen),
                contenidoMensaje=contenido.get("contenidoMensaje", str(contenido))
            )
        else:
            # Si el contenido es texto plano
            mensaje_dto = MensajeDTO(
                nombreUsuario=paquete.origen,
                contenidoMensaje=str(contenido)
            )

        self._logger.info(f"Mensaje grupal recibido de {mensaje_dto.nombreUsuario}: {mensaje_dto.contenidoMensaje}")

        # Notificar a ModeloChatTCP
        if self._modelo_chat_tcp:
            # Convertir MensajeDTO a UsuarioOP
            usuario_op = UsuarioOP(
                nombre=mensaje_dto.nombreUsuario,
                ip="",
                puerto=0,
                ultimo_mensaje=mensaje_dto.contenidoMensaje
            )

            # Notificar a través de ModeloChatTCP
            self._modelo_chat_tcp.notificar(usuario_op)
