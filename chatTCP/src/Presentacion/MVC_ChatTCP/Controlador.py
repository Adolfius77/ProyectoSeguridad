"""CONTROLADOR SOLO MANDA ACIONES QUE EXISTEN EN EL MODELOCHATTCP DEL MVC """
# CONSTRUCTOR OKUPA UN MODELOCHATTCP
#VISTAS LLAMA AL CONTROLADOR

class Controlador:

    def __init__(self, modeloChatTCP):
        # Guardamos el modelo en un atributo
        self.modelo = modeloChatTCP

    def iniciarSesion(self, nombreUsuario, contrasena):
        self.modelo.iniciar_sesion(nombreUsuario, contrasena)

    def registrarUsuario(self, nombreUsuario, contrasena):
        self.modelo.registrar_usuario(nombreUsuario, contrasena)

    #metodo de menu users
    def abrir_chat_controlador(self,usuarioOP):
        self.modelo.mostrar_chat(usuarioOP)

    def enviar_mensaje(self, mensaje_texto, usuario_destino):
        if mensaje_texto and usuario_destino:
            self.modelo.enviar_mensaje(mensaje_texto, usuario_destino)