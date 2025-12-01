#clase que representa un mensaje enviado por un usuario
#En presentacion el usuario nomas va a enviar un String un msj pelon

from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MensajeDTO:

    nombreUsuario: str
    contenidoMensaje: str
    fechaHora: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"[{self.fechaHora}] {self.nombreUsuario}: {self.contenidoMensaje}"
