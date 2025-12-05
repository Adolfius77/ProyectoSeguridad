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

    #metodo de menu users
    def abrir_chat_controlador(self,usuarioOP):
        self.modelo.mostrar_chat(usuarioOP)

    def enviar_mensaje_privado(self, usuario_destino, contenido: str) -> None:
        """
        Delega el envío de mensaje privado al modelo.
        """
        self.modelo.enviar_mensaje_privado(usuario_destino, contenido)

    def enviar_mensaje_grupal(self, contenido: str) -> None:
        """
        Delega el envío de mensaje grupal al modelo.
        """
        self.modelo.enviar_mensaje_grupal(contenido)

    def unirse_chat(self, nombre_chat: str) -> None:
        """
        Delega la acción de unirse a un chat.
        """
        self.modelo.unirse_chat(nombre_chat)

    def registrar_en_eventbus(self, host_bus: str, puerto_bus: int) -> None:
        """
        Delega el registro en EventBus.
        """
        self.modelo.registrar_en_eventbus(host_bus, puerto_bus)

    def desconectar(self) -> None:
        """
        Delega la desconexión.
        """
        self.modelo.desconectar()