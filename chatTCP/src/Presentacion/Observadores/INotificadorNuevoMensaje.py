from abc import ABC, abstractmethod
from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuariosOP

class INotificadorNuevoMensaje(ABC):
    """
    Interfaz para el patrón Observer (Observer/Subscriber).
    Los objetos que implementen esta interfaz podrán recibir notificaciones
    cuando haya un nuevo mensaje para un usuario.
    """

    @abstractmethod
    def actualizar(self, usuario_op: UsuariosOP):
        """
        Método llamado por el publicador cuando hay un cambio en un usuario.

        Args:
            usuario_op: UsuarioOP con información actualizada (nombre, último mensaje,
                       color, total de mensajes nuevos)
        """
        pass
