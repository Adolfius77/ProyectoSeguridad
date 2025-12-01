"""
Interfaz Observable para envíos de red
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ObservadorEnvios import ObservadorEnvios


class ObservableEnvios(ABC):
    """
    Interfaz para objetos observables que notifican cuando hay datos para enviar
    """

    @abstractmethod
    def agregar_observador(self, observador: 'ObservadorEnvios') -> None:
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
