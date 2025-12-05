import json
import os
import threading
from ..Red.Cifrado.seguridad import GestorSeguridad

ARCHIVO = "usuarios.json"
lock_usuarios = threading.Lock()


class repositorioUsuarios:
    @staticmethod
    def guardar(usuario, password_raw):
        with lock_usuarios:
            datos = {}
            if os.path.exists(ARCHIVO):
                try:
                    with open(ARCHIVO, "r") as f:
                        datos = json.load(f)
                except json.JSONDecodeError:
                    datos = {}
            # validar duplicado
            if usuario in datos: return False

            # hashear y guardar :0
            phash = GestorSeguridad().hash_password(password_raw)
            datos[usuario] = phash

            with open(ARCHIVO, "w") as f:
                json.dump(datos, f)
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
