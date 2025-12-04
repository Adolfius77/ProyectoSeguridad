"""
Receptor de prueba para el EnsambladorRed
Imprime los paquetes recibidos en consola
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ComponenteReceptor.IReceptor import IReceptor
from src.ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO


class ReceptorPrueba(IReceptor):
    """
    Receptor simple que imprime los paquetes recibidos
    """

    def __init__(self, nombre: str = "Receptor"):
        self.nombre = nombre
        self.paquetes_recibidos = []

    def recibir_cambio(self, paquete: PaqueteDTO) -> None:
        """
        Procesa un paquete recibido de la red

        Args:
            paquete: PaqueteDTO recibido
        """
        print(f"\n[{self.nombre}] Paquete recibido:")
        print(f"  - Tipo: {paquete.tipo}")
        print(f"  - Contenido: {paquete.contenido}")
        print(f"  - Origen: {paquete.origen}")
        print(f"  - Destino: {paquete.destino}")
        print(f"  - Puerto origen: {paquete.puerto_origen}")
        print(f"  - Puerto destino: {paquete.puerto_destino}")

        self.paquetes_recibidos.append(paquete)
