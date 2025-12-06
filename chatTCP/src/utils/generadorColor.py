#Clase singleton que genera colores random y los setea al usuarioDTO antes de ser enviado a guardarse en el Json
import random

class GeneradorColor:
    _instancia = None
    _colores_usados = set()

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(GeneradorColor, cls).__new__(cls)
        return cls._instancia

    def generar_color_unico(self):
        """Genera un color HEX aleatorio que no se repita."""
        if len(self._colores_usados) >= 0xFFFFFF:
            raise Exception("Ya no hay colores disponibles.")

        while True:
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            if color not in self._colores_usados:
                self._colores_usados.add(color)
                return color

    def asignar_color_a_usuario(self, usuarioDTO):
        """Asigna un color único al usuarioDTO."""
        usuarioDTO.color = self.generar_color_unico()
        return usuarioDTO
