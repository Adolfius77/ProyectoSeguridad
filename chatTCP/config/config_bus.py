"""
Configuración del EventBus
"""


class ConfigBus:
    """
    Configuración para el EventBus y servicios de red
    """

    # Configuración del EventBus
    HOST = "localhost"
    PUERTO_ENTRADA = 5555  # Puerto donde el EventBus recibe eventos
    PUERTO_BUS = 5556      # Puerto desde donde el EventBus envía eventos

    # Buffer de red
    BUFFER_SIZE = 4096

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def get_config(cls) -> dict:
        """
        Obtiene la configuración como diccionario

        Returns:
            Diccionario con la configuración
        """
        return {
            'host': cls.HOST,
            'puerto_entrada': cls.PUERTO_ENTRADA,
            'puerto_bus': cls.PUERTO_BUS,
            'buffer_size': cls.BUFFER_SIZE,
            'log_level': cls.LOG_LEVEL,
            'log_format': cls.LOG_FORMAT
        }
