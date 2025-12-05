"""
Clase que implementa IReceptor.
Aquí le llegan los diferentes tipos de eventos de la red y los delega a LogicaChatTCP.
"""
import logging
from typing import Optional, TYPE_CHECKING
from chatTCP.src.ComponenteReceptor.IReceptor import IReceptor
from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

if TYPE_CHECKING:
    from chatTCP.src.ModeloChatTCP.ChatTCP.LogicaChatTCP import LogicaChatTCP


class ReceptorMensaje(IReceptor):
    """
    Receptor de mensajes que implementa la interfaz IReceptor.

    Este componente:
    - Recibe paquetes de la red (vía EnsambladorRed/PublicadorEventos)
    - Delega el procesamiento a LogicaChatTCP
    - Actúa como adaptador entre la capa de red y la lógica de negocio
    """

    def __init__(self, logica_chat: Optional['LogicaChatTCP'] = None):
        """
        Inicializa el receptor de mensajes.

        Args:
            logica_chat: Instancia de LogicaChatTCP que procesará los eventos (opcional)
        """
        self._logica_chat = logica_chat
        self._logger = logging.getLogger(__name__)

        self._logger.info("ReceptorMensaje inicializado")

    def set_logica_chat(self, logica_chat: 'LogicaChatTCP') -> None:
        """
        Configura la instancia de LogicaChatTCP que procesará los eventos.

        Args:
            logica_chat: Instancia de LogicaChatTCP
        """
        self._logica_chat = logica_chat
        self._logger.info("LogicaChatTCP configurada en ReceptorMensaje")

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        """
        Método de la interfaz IReceptor.
        Recibe un paquete de la red y lo procesa.

        Args:
            paquete: Paquete recibido de la red
        """
        if paquete is None:
            self._logger.warning("Paquete None recibido, ignorando")
            return

        self._logger.info(f"[ReceptorMensaje] Paquete recibido: tipo={paquete.tipo}, origen={paquete.origen}")

        # Si no hay LogicaChatTCP configurada, solo logueamos
        if self._logica_chat is None:
            self._logger.warning(f"LogicaChatTCP no configurada. Evento tipo '{paquete.tipo}' no procesado")
            return

        try:
            # Delegar el procesamiento a LogicaChatTCP
            self._logica_chat.procesarEvento(paquete)

        except Exception as e:
            self._logger.error(f"Error al procesar paquete en ReceptorMensaje: {e}", exc_info=True)

    def get_logica_chat(self) -> Optional['LogicaChatTCP']:
        """
        Obtiene la instancia de LogicaChatTCP configurada.

        Returns:
            LogicaChatTCP o None si no está configurada
        """
        return self._logica_chat
