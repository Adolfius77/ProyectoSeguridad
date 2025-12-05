from abc import ABC, abstractmethod
from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuariosOP

class IPublicadorNuevoMensaje(ABC):
    """
    Interfaz para el patrón Observer (Publisher/Subject).
    Permite agregar observadores y notificarles cuando hay un nuevo mensaje.
    """

    @abstractmethod
    def agregar_observador(self, observador):
        """
        Agrega un observador a la lista de suscriptores.

        Args:
            observador: Objeto que implementa INotificadorNuevoMensaje
        """
        pass

    @abstractmethod
    def remover_observador(self, observador):
        """
        Remueve un observador de la lista de suscriptores.

        Args:
            observador: Objeto que implementa INotificadorNuevoMensaje
        """
        pass

    @abstractmethod
    def notificar(self, usuario_op: UsuariosOP):
        """
        Notifica a todos los observadores sobre un cambio en un usuario.

        Args:
            usuario_op: UsuarioOP con información actualizada
        """
        pass
