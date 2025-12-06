import json
import os
import threading

from ..ModeloChatTCP.DTOs.UsuarioDTO import UsuarioDTO
from ..Red.Cifrado.seguridad import GestorSeguridad

ARCHIVO = "usuarios.json"
lock_usuarios = threading.Lock()


class repositorioUsuarios:
    @staticmethod
    def guardar(usuario_dto: UsuarioDTO):
        with lock_usuarios:
            datos = {}

            # Leer JSON si existe
            if os.path.exists(ARCHIVO):
                try:
                    with open(ARCHIVO, "r", encoding="utf-8") as f:
                        datos = json.load(f)
                except json.JSONDecodeError:
                    datos = {}

            # Validar duplicado
            if usuario_dto.nombre_usuario in datos:
                return False

            # Hashear contraseña antes de guardarla
            hash_pwd = GestorSeguridad().hash_password(usuario_dto.contrasena)

            # Convertir DTO a diccionario serializable
            datos[usuario_dto.nombre_usuario] = {
                "contrasena": hash_pwd,
                "ip": usuario_dto.ip,
                "puerto": usuario_dto.puerto,
                "color": usuario_dto.color,
                "public_key": usuario_dto.public_key
            }

            # Guardar archivo JSON
            with open(ARCHIVO, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4)

            return True

    @staticmethod
    def validar(usuario, password_raw):
        with lock_usuarios:
            if not os.path.exists(ARCHIVO): return False
            try:
                with open(ARCHIVO, "r") as f:
                    datos = json.load(f)
            except:
                return False

            phash = GestorSeguridad().hash_password(password_raw)
            return datos.get(usuario) == phash


    @staticmethod
    def obtener_usuario(usuario_nombre):
        if not os.path.exists(ARCHIVO):
            return None

        with open(ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if usuario_nombre not in datos:
            return None

        u = datos[usuario_nombre]

        return UsuarioDTO(
            nombre_usuario=usuario_nombre,
            contrasena=u["contrasena"],
            ip=u["ip"],
            puerto=u["puerto"],
            color=u["color"],
            public_key=u["public_key"]
        )