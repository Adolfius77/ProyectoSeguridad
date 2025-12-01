"""
PaqueteDTO: Clase que representa información enviada por red en formato JSON
Compatible con arquitectura EventBus
"""
import json
from typing import Any, Optional


class PaqueteDTO:
    """
    Representa un paquete de datos para transmisión por red
    Incluye información de enrutamiento (origen, destino) y tipo de evento
    """

    def __init__(
        self,
        tipo: str,
        contenido: Any,
        origen: Optional[str] = None,
        destino: Optional[str] = None,
        host: Optional[str] = None,
        puerto_origen: Optional[int] = None,
        puerto_destino: Optional[int] = None
    ):
        """
        Inicializa un paquete de red

        Args:
            tipo: Tipo de evento o mensaje
            contenido: Datos del paquete (puede ser cualquier objeto serializable)
            origen: Identificador del origen
            destino: Identificador del destino
            host: Host de red
            puerto_origen: Puerto de origen
            puerto_destino: Puerto de destino
        """
        self.tipo = tipo
        self.contenido = contenido
        self.origen = origen
        self.destino = destino
        self.host = host
        self.puerto_origen = puerto_origen
        self.puerto_destino = puerto_destino

    def to_json(self) -> str:
        """
        Serializa el paquete a formato JSON

        Returns:
            String JSON representando el paquete
        """
        return json.dumps(self.__dict__, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> 'PaqueteDTO':
        """
        Deserializa un paquete desde formato JSON

        Args:
            json_str: String JSON a deserializar

        Returns:
            Instancia de PaqueteDTO
        """
        data = json.loads(json_str)
        return PaqueteDTO(
            tipo=data['tipo'],
            contenido=data['contenido'],
            origen=data.get('origen'),
            destino=data.get('destino'),
            host=data.get('host'),
            puerto_origen=data.get('puerto_origen'),
            puerto_destino=data.get('puerto_destino')
        )

    def __str__(self) -> str:
        """
        Representación en string del paquete

        Returns:
            String describiendo el paquete
        """
        return f"PaqueteDTO(tipo={self.tipo}, origen={self.origen}, destino={self.destino})"

    def __repr__(self) -> str:
        """
        Representación detallada del paquete

        Returns:
            String con representación completa
        """
        return self.__str__()
    