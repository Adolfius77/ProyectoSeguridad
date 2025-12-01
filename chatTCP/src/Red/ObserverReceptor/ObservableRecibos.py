"""
Interfaz Observable para recepción de red
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ObservadorRecibos import ObservadorRecibos


class ObservableRecibos(ABC):
    """
    Interfaz para objetos observables que notifican cuando se reciben datos
    """

    @abstractmethod
    def agregar_observador(self, observador: 'ObservadorRecibos') -> None:
        """
        Agrega un observador a la lista de observadores

        Args:
            observador: El observador a agregar
        """
        pass

    @abstractmethod
    def notificar(self) -> None:
        """
        Notifica a todos los observadores registrados
        """
        pass
