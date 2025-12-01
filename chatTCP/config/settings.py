"""
Configuración general de la aplicación
"""


class Settings:
    """
    Clase para manejar la configuración de la aplicación
    """

    def __init__(self):
        self.host = "localhost"
        self.port = 5000
        self.buffer_size = 1024
        self.encryption_enabled = True

    @classmethod
    def load_from_file(cls, config_file: str):
        """
        Carga configuración desde un archivo
        """
        pass
