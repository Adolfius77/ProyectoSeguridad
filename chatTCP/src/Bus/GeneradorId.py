class GeneradorId:
    """
    Singleton que genera IDs incrementales para servicios.
    """
    _instancia = None
    _contador = 0

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def generar(self) -> int:
        """
        Devuelve un ID incremental único.
        """
        self._contador += 1
        return self._contador
