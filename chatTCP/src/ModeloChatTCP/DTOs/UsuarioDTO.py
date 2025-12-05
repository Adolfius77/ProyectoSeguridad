"""
Clase que representa a un usuario conectado en el sistema.
Contiene información de identificación, conexión y presentación del usuario.
"""
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class UsuarioDTO:
    """
    Data Transfer Object para usuarios del sistema de chat TCP.

    Attributes:
        nombre_usuario: Nombre único de identificación del usuario
        contrasena: Contraseña del usuario (debe ser hasheada en producción)
        ip: Dirección IP del usuario
        puerto: Puerto en el que el usuario escucha conexiones
        color: Color hexadecimal único asignado al usuario (ej: #F54242)
        public_key: Llave pública del usuario para cifrado (opcional)
    """
    nombre_usuario: str
    contrasena: str
    ip: str
    puerto: int
    color: str = ""
    public_key: Optional[str] = None

    def __post_init__(self):
        """Genera un color aleatorio si no se proporcionó uno"""
        if not self.color:
            self.color = self._generar_color_aleatorio()

    @staticmethod
    def _generar_color_aleatorio() -> str:
        """
        Genera un color hexadecimal aleatorio.

        Returns:
            String con formato hexadecimal (ej: #A3F542)
        """
        # Generar componentes RGB aleatorios
        r = random.randint(60, 255)  # Evitar colores muy oscuros
        g = random.randint(60, 255)
        b = random.randint(60, 255)

        return f"#{r:02X}{g:02X}{b:02X}"

    def __str__(self):
        return f"Usuario({self.nombre_usuario}@{self.ip}:{self.puerto})"

    def __repr__(self):
        return self.__str__()

    def sin_contrasena(self):
        """
        Retorna una copia del UsuarioDTO sin la contraseña.
        Útil para enviar información del usuario sin exponer datos sensibles.

        Returns:
            UsuarioDTO con contraseña vacía
        """
        return UsuarioDTO(
            nombre_usuario=self.nombre_usuario,
            contrasena="",
            ip=self.ip,
            puerto=self.puerto,
            color=self.color,
            public_key=self.public_key
        )


class GeneradorColoresUnicos:
    """
    Clase auxiliar para generar colores únicos sin repetición.
    Útil cuando se necesita asignar colores diferentes a múltiples usuarios.
    """

    def __init__(self):
        self._colores_usados = set()
        self._max_intentos = 100

    def generar_color_unico(self) -> str:
        """
        Genera un color hexadecimal que no ha sido usado previamente.

        Returns:
            String con formato hexadecimal único

        Raises:
            RuntimeError: Si no se puede generar un color único después de max_intentos
        """
        for _ in range(self._max_intentos):
            color = UsuarioDTO._generar_color_aleatorio()
            if color not in self._colores_usados:
                self._colores_usados.add(color)
                return color

        raise RuntimeError(f"No se pudo generar un color único después de {self._max_intentos} intentos")

    def liberar_color(self, color: str):
        """
        Marca un color como disponible nuevamente.

        Args:
            color: Color hexadecimal a liberar
        """
        self._colores_usados.discard(color)

    def limpiar(self):
        """Limpia todos los colores usados"""
        self._colores_usados.clear()
