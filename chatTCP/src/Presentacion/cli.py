"""
Interfaz de línea de comandos para el chat TCP
"""


class ChatCLI:
    """
    Clase para manejar la interfaz de usuario por consola
    """

    def __init__(self):
        pass

    def start(self):
        """
        Inicia la interfaz de usuario
        """
        pass

    def display_message(self, message: str):
        """
        Muestra un mensaje en la consola
        """
        print(f"[Chat] {message}")

    def get_user_input(self, prompt: str = "> ") -> str:
        """
        Obtiene entrada del usuario
        """
        return input(prompt)
