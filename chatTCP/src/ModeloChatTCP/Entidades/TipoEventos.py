#Tipo de eventos que recibira el ReceptorMensajes
#Enum

from enum import Enum

class TiposEvento(str, Enum):
    iniciarConexion = "INICIAR_CONEXION"
    unirseChat = "UNIRSE_CHAT" #evento enviado para unirse al chatGrupal
    unirseGrupal = "UNIRSE_GRUPAL" #evento para suscribirse a mensajes grupales
    mensajePrivado = "MENSAJE_PRIVADO" #
    mensajeGrupal = "MENSAJE_GRUPAL"



