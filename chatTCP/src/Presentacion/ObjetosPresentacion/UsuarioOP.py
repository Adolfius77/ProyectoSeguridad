#clase que representa a un usuario Presentacion
#puede tener una imagen de user, nombre user, color del user, etc

class UsuariosOP:
    def __init__(self, nombre, ultimo_mensaje, color,totalMsjNuevos):
        self.nombre = nombre
        self.ultimo_mensaje = ultimo_mensaje
        self.color = color  # color hexa
        self.totalMsjNuevos = totalMsjNuevos