"""
Módulo de validaciones para el sistema ChatTCP.

Contiene todas las validaciones extraídas de las interfaces gráficas
para centralizar la lógica de validación y permitir reutilización.
"""
import re
from typing import Tuple


class ValidacionError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class ValidadorUsuario:
    """
    Validador para datos de usuario (registro y login).

    Centraliza todas las reglas de negocio relacionadas con usuarios.
    """

    # Constantes de configuración
    MIN_LONGITUD_USUARIO = 3
    MAX_LONGITUD_USUARIO = 20
    MIN_LONGITUD_CONTRASENA = 6

    # Patrones regex
    PATRON_USUARIO_VALIDO = r'^[a-zA-Z0-9_-]+$'
    PATRON_MINUSCULA = r'[a-z]'
    PATRON_MAYUSCULA = r'[A-Z]'
    PATRON_NUMERO = r'[0-9]'

    @staticmethod
    def validar_campo_vacio(valor: str, nombre_campo: str) -> None:
        """
        Valida que un campo no esté vacío o contenga solo espacios.

        Args:
            valor: Valor del campo a validar
            nombre_campo: Nombre del campo para mensajes de error

        Raises:
            ValidacionError: Si el campo está vacío o contiene solo espacios
        """
        if not valor:
            raise ValidacionError(f"{nombre_campo} no puede estar vacío")

        if valor.isspace():
            raise ValidacionError(f"{nombre_campo} no puede contener solo espacios")

    @staticmethod
    def validar_usuario(usuario: str) -> None:
        """
        Valida el nombre de usuario según las reglas de negocio.

        Reglas:
        - No puede estar vacío o contener solo espacios
        - Debe tener entre 3 y 20 caracteres
        - Solo puede contener letras, números, guiones y guiones bajos

        Args:
            usuario: Nombre de usuario a validar

        Raises:
            ValidacionError: Si el usuario no cumple las reglas
        """
        # Validar vacío y espacios
        ValidadorUsuario.validar_campo_vacio(usuario, "El usuario")

        # Eliminar espacios al inicio y final
        usuario = usuario.strip()

        # Validar longitud
        if len(usuario) < ValidadorUsuario.MIN_LONGITUD_USUARIO:
            raise ValidacionError(
                f"El usuario debe tener al menos {ValidadorUsuario.MIN_LONGITUD_USUARIO} caracteres"
            )

        if len(usuario) > ValidadorUsuario.MAX_LONGITUD_USUARIO:
            raise ValidacionError(
                f"El usuario no puede tener más de {ValidadorUsuario.MAX_LONGITUD_USUARIO} caracteres"
            )

        # Validar caracteres permitidos
        if not re.match(ValidadorUsuario.PATRON_USUARIO_VALIDO, usuario):
            raise ValidacionError(
                "El usuario solo puede contener letras, números, guiones y guiones bajos"
            )

    @staticmethod
    def validar_contrasena(contrasena: str, strict: bool = False) -> Tuple[bool, str]:
        """
        Valida la contraseña según las reglas de seguridad.

        Reglas:
        - No puede estar vacía o contener solo espacios
        - Debe tener al menos 6 caracteres
        - Debe contener al menos una minúscula (advertencia)
        - Debe contener al menos una mayúscula (advertencia)
        - Debe contener al menos un número (advertencia)

        Args:
            contrasena: Contraseña a validar
            strict: Si es True, las reglas de contraseña fuerte son obligatorias.
                   Si es False, solo muestra advertencias (modo permisivo)

        Returns:
            Tuple[bool, str]: (es_valida, mensaje)
                - es_valida: True si cumple todas las reglas, False si falla alguna
                - mensaje: Descripción del resultado o error

        Raises:
            ValidacionError: Si falla validaciones básicas (vacía, muy corta)
        """
        # Validar vacío y espacios
        try:
            ValidadorUsuario.validar_campo_vacio(contrasena, "La contraseña")
        except ValidacionError as e:
            if strict:
                raise
            return False, str(e)

        # Validar longitud mínima (siempre obligatoria)
        if len(contrasena) < ValidadorUsuario.MIN_LONGITUD_CONTRASENA:
            mensaje = f"La contraseña debe tener al menos {ValidadorUsuario.MIN_LONGITUD_CONTRASENA} caracteres"
            if strict:
                raise ValidacionError(mensaje)
            return False, mensaje

        # Validaciones de contraseña fuerte
        if not re.search(ValidadorUsuario.PATRON_MINUSCULA, contrasena):
            mensaje = "La contraseña debe contener al menos una letra minúscula"
            if strict:
                raise ValidacionError(mensaje)
            return False, mensaje

        if not re.search(ValidadorUsuario.PATRON_MAYUSCULA, contrasena):
            mensaje = "La contraseña debe contener al menos una letra mayúscula"
            if strict:
                raise ValidacionError(mensaje)
            return False, mensaje

        if not re.search(ValidadorUsuario.PATRON_NUMERO, contrasena):
            mensaje = "La contraseña debe contener al menos un número"
            if strict:
                raise ValidacionError(mensaje)
            return False, mensaje

        return True, "Contraseña segura"

    @staticmethod
    def validar_contrasenas_coinciden(contrasena: str, confirmacion: str) -> None:
        """
        Valida que dos contraseñas coincidan.

        Args:
            contrasena: Contraseña original
            confirmacion: Confirmación de contraseña

        Raises:
            ValidacionError: Si las contraseñas no coinciden
        """
        if contrasena != confirmacion:
            raise ValidacionError("Las contraseñas no coinciden")

    @staticmethod
    def validar_login(usuario: str, contrasena: str) -> None:
        """
        Valida los datos de login.

        Args:
            usuario: Nombre de usuario
            contrasena: Contraseña

        Raises:
            ValidacionError: Si algún campo no es válido
        """
        # Solo validar que no estén vacíos para login
        ValidadorUsuario.validar_campo_vacio(usuario, "El usuario")
        ValidadorUsuario.validar_campo_vacio(contrasena, "La contraseña")

    @staticmethod
    def validar_registro(usuario: str, contrasena: str, confirmacion: str, strict_password: bool = False) -> Tuple[bool, str]:
        """
        Valida los datos de registro de un nuevo usuario.

        Args:
            usuario: Nombre de usuario
            contrasena: Contraseña
            confirmacion: Confirmación de contraseña
            strict_password: Si True, requiere contraseña fuerte obligatoriamente

        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
                - es_valido: True si todo es válido
                - mensaje: Descripción del resultado o advertencia

        Raises:
            ValidacionError: Si las validaciones básicas fallan
        """
        # Validar usuario
        ValidadorUsuario.validar_usuario(usuario)

        # Validar que las contraseñas coincidan
        ValidadorUsuario.validar_contrasenas_coinciden(contrasena, confirmacion)

        # Validar fortaleza de contraseña
        es_fuerte, mensaje = ValidadorUsuario.validar_contrasena(contrasena, strict=strict_password)

        return es_fuerte, mensaje


class ValidadorMensaje:
    """
    Validador para mensajes del chat.
    """

    MAX_LONGITUD_MENSAJE = 1000

    @staticmethod
    def validar_mensaje(mensaje: str) -> None:
        """
        Valida un mensaje de chat.

        Args:
            mensaje: Contenido del mensaje

        Raises:
            ValidacionError: Si el mensaje no es válido
        """
        if not mensaje or mensaje.isspace():
            raise ValidacionError("El mensaje no puede estar vacío")

        if len(mensaje) > ValidadorMensaje.MAX_LONGITUD_MENSAJE:
            raise ValidacionError(
                f"El mensaje no puede exceder {ValidadorMensaje.MAX_LONGITUD_MENSAJE} caracteres"
            )


# Funciones de utilidad para compatibilidad con código existente
def validar_contrasena_fuerte(contrasena: str) -> Tuple[bool, str]:
    """
    Función de compatibilidad para interfaces existentes.

    Extraída de: interfazRegistroUsuario.py (líneas 41-46)

    Args:
        contrasena: Contraseña a validar

    Returns:
        Tuple[bool, str]: (es_fuerte, mensaje)
    """
    return ValidadorUsuario.validar_contrasena(contrasena, strict=False)


def validar_usuario_valido(usuario: str) -> bool:
    """
    Función de compatibilidad para interfaces existentes.

    Extraída de: interfazRegistroUsuario.py (líneas 48-50)

    Args:
        usuario: Usuario a validar

    Returns:
        bool: True si el usuario cumple el patrón, False en caso contrario
    """
    return bool(re.match(ValidadorUsuario.PATRON_USUARIO_VALIDO, usuario))
