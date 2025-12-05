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