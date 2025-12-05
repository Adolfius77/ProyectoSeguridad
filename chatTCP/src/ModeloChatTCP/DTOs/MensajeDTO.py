"""
Clase que representa un mensaje enviado por un usuario.
En presentación el usuario solo envía un String (mensaje simple).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from chatTCP.src.ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO
from chatTCP.src.Presentacion.ObjetosPresentacion import UsuarioOP



@dataclass
class MensajeDTO:
    """
    Data Transfer Object para mensajes del chat.

    Attributes:
        nombreUsuario: Nombre del usuario que envía el mensaje
        contenidoMensaje: Texto del mensaje
        fechaHora: Timestamp de cuando se creó el mensaje
        usuario: Objeto UsuarioDTO completo del remitente (opcional)
    """
    nombreUsuario: str
    contenidoMensaje: str
    fechaHora: datetime = field(default_factory=datetime.now)
    usuarioDestino: Optional[UsuarioOP] = None #usuario a quien se le envia
    usuarioOrigen: Optional[UsuarioDTO] = None


    def __str__(self):
        return f"[{self.fechaHora.strftime('%H:%M:%S')}] {self.nombreUsuario}: {self.contenidoMensaje}"


    def to_dict(self):
        return {
            "nombreUsuario": self.nombreUsuario,
            "contenidoMensaje": self.contenidoMensaje,
            "fechaHora": self.fechaHora.isoformat(),
            "usuario": str(self.usuario) if self.usuario else None
            "usuarioDestino": self.usuarioDestino.to_dict(),
            "usuarioOrigen": self.usuarioOrigen.to_dict()
        }
