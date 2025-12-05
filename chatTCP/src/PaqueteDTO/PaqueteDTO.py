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
            puerto_destino: Optional[int] = None,
            llave_publica_origen: Optional[bytes] = None
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
            llave_publica_origen: Llave pública RSA del origen (en bytes)
        """
        self.tipo = tipo
        self.contenido = contenido
        self.origen = origen
        self.destino = destino
        self.host = host
        self.puerto_origen = puerto_origen
        self.puerto_destino = puerto_destino
        self.llave_publica_origen = llave_publica_origen

    def to_json(self) -> str:
        """
        Serializa el paquete a formato JSON

        Nota: llave_publica_origen se codifica en base64 para serialización JSON

        Returns:
            String JSON representando el paquete
        """
        import base64
        data = self.__dict__.copy()

        # Convertir llave pública a base64 si existe
        if data.get('llave_publica_origen'):
            data['llave_publica_origen'] = base64.b64encode(data['llave_publica_origen']).decode('utf-8')

        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> 'PaqueteDTO':
        """
        Deserializa un paquete desde formato JSON

        Nota: llave_publica_origen se decodifica desde base64

        Args:
            json_str: String JSON a deserializar

        Returns:
            Instancia de PaqueteDTO
        """
        import base64
        data = json.loads(json_str)

        # Decodificar llave pública desde base64 si existe
        llave_publica = data.get('llave_publica_origen')
        if llave_publica and isinstance(llave_publica, str):
            llave_publica = base64.b64decode(llave_publica)

        return PaqueteDTO(
            tipo=data['tipo'],
            contenido=data['contenido'],
            origen=data.get('origen'),
            destino=data.get('destino'),
            host=data.get('host'),
            puerto_origen=data.get('puerto_origen'),
            puerto_destino=data.get('puerto_destino'),
            llave_publica_origen=llave_publica
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
