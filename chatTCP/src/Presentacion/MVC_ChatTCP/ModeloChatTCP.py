"""
SE CONECTA CON LA CARPETA MODELOCHATTCP
AQUI VA LA LOGICA DE VALIDACIONES, REGLAS DE NEGOCIO, ETC
"""

class ModeloChatTCP:

    def __init__(self, chatTCP):
        # Guardamos el componente real que ejecuta la lógica de red
        self.logicaChatTCP = chatTCP

    def iniciar_sesion(self, nombre_usuario, contrasena):
        print(f"[Modelo] Iniciando sesión para: {nombre_usuario}")
        # Aquí irían validaciones y luego lógica de red:
        # self.logicaChatTCP.enviar_paquete(...)
        # self.logicaChatTCP.autenticar(...)

    def registrar_usuario(self, nombre_usuario, contrasena):
        print(f"[Modelo] Registrando usuario: {nombre_usuario}")
        # Aquí va la lógica real de registro
        # self.logicaChatTCP.registrar(...)
