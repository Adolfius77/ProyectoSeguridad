"""CONTROLADOR SOLO MANDA ACIONES QUE EXISTEN EN EL MODELOCHATTCP DEL MVC """
# CONSTRUCTOR OKUPA UN MODELOCHATTCP
#VISTAS LLAMA AL CONTROLADOR

class Controlador:

    def __init__(self, modeloChatTCP):
        # Guardamos el modelo en un atributo
        self.modelo = modeloChatTCP

    def iniciarSesion(self, nombreUsuario, contrasena):
        """
        La vista llama al controlador,
        y el controlador usa la función del modelo.
        """
        self.modelo.iniciar_sesion(nombreUsuario, contrasena)

    def registrarUsuario(self, nombreUsuario, contrasena):
        """
        Delegar la acción al modelo.
        """
        self.modelo.registrar_usuario(nombreUsuario, contrasena)