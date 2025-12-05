"""
SE CONECTA CON LA CARPETA MODELOCHATTCP
AQUI VA LA LOGICA DE VALIDACIONES, REGLAS DE NEGOCIO, ETC
"""

from chatTCP.src.Presentacion.Observadores.IPublicadorNuevoMensaje import IPublicadorNuevoMensaje
from chatTCP.src.Presentacion.Observadores.INotificadorNuevoMensaje import INotificadorNuevoMensaje
from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuariosOP

class ModeloChatTCP(IPublicadorNuevoMensaje):

    def __init__(self, chatTCP):
        # Guardamos el componente real que ejecuta la lógica de red
        self.logicaChatTCP = chatTCP
        # Lista de observadores para el patrón Observer
        self._observadores = []

        # Configurar la referencia de LogicaChatTCP a este ModeloChatTCP
        self.logicaChatTCP.set_modelo_chat_tcp(self)

    def iniciar_sesion(self, nombre_usuario, contrasena):
        print(f"[Modelo] Iniciando sesión para: {nombre_usuario}")
        # Aquí irían validaciones y luego lógica de red:
        # self.logicaChatTCP.enviar_paquete(...)
        # self.logicaChatTCP.autenticar(...)

    def registrar_usuario(self, nombre_usuario, contrasena):
        print(f"[Modelo] Registrando usuario: {nombre_usuario}")
        # Aquí va la lógica real de registro
        # self.logicaChatTCP.registrar(...)


    def mostrar_chat(self, usuarioOP):
        """
        Abre el formulario de chat para un usuario específico.

        Args:
            usuarioOP: UsuarioOP del usuario con el que se abrirá el chat
        """
        print(f"[Modelo] Abriendo chat con: {usuarioOP.nombre}")
        # Aquí va la lógica para abrir el chat

    # ========== Métodos de envío de mensajes ==========

    def enviar_mensaje_privado(self, usuario_destino: UsuariosOP, contenido: str) -> None:
        """
        Envía un mensaje privado a un usuario específico.

        Args:
            usuario_destino: UsuarioOP del destinatario
            contenido: Texto del mensaje a enviar
        """
        print(f"[Modelo] Enviando mensaje privado a {usuario_destino.nombre}: {contenido}")
        self.logicaChatTCP.enviarMensajePrivado(usuario_destino, contenido)

    def enviar_mensaje_grupal(self, contenido: str) -> None:
        """
        Envía un mensaje grupal (broadcast) a todos los usuarios.

        Args:
            contenido: Texto del mensaje a enviar
        """
        print(f"[Modelo] Enviando mensaje grupal: {contenido}")
        self.logicaChatTCP.enviarMensajeGrupal(contenido)

    def registrar_en_eventbus(self, host_bus: str, puerto_bus: int) -> None:
        """
        Registra el usuario en el EventBus.

        Args:
            host_bus: Host del EventBus
            puerto_bus: Puerto del EventBus
        """
        print(f"[Modelo] Registrándose en EventBus: {host_bus}:{puerto_bus}")
        self.logicaChatTCP.registrarseEnEventBus(host_bus, puerto_bus)

    def desconectar(self) -> None:
        """
        Envía notificación de desconexión.
        """
        print("[Modelo] Desconectando usuario")
        self.logicaChatTCP.desconectar()

    # ========== Métodos de IPublicadorNuevoMensaje ==========

    def agregar_observador(self, observador: INotificadorNuevoMensaje):
        """
        Agrega un observador a la lista de suscriptores.

        Args:
            observador: Objeto que implementa INotificadorNuevoMensaje
        """
        if observador not in self._observadores:
            self._observadores.append(observador)
            print(f"[Modelo] Observador agregado. Total: {len(self._observadores)}")

    def remover_observador(self, observador: INotificadorNuevoMensaje):
        """
        Remueve un observador de la lista de suscriptores.

        Args:
            observador: Objeto que implementa INotificadorNuevoMensaje
        """
        if observador in self._observadores:
            self._observadores.remove(observador)
            print(f"[Modelo] Observador removido. Total: {len(self._observadores)}")

    def notificar(self, usuario_op: UsuariosOP):
        """
        Notifica a todos los observadores sobre un cambio en un usuario.
        Este método se llama cuando hay un nuevo mensaje para un usuario.

        Args:
            usuario_op: UsuarioOP con información actualizada
        """
        print(f"[Modelo] Notificando a {len(self._observadores)} observadores sobre cambio en {usuario_op.nombre}")
        for observador in self._observadores:
            observador.actualizar(usuario_op)

#Metodo de enviar msj se pasal el usuarioLogin y se pasa el UsuarioObjPresentacion