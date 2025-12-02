import json
import os

from ..Red.Cifrado.seguridad import GestorSeguridad

ARCHIVO = "usuarios.json"
class repositorioUsuarios:
    @staticmethod
    def guardar(usuario, password_raw):
        datos = {}
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r") as f: datos = json.load(f)

        #validar duplicado
        if usuario in datos: return False

        #hashear y guardar :0
        phash = GestorSeguridad().hash_password(password_raw)
        datos[usuario] = phash

        with open(ARCHIVO, "w") as f: json.dump(datos, f)
        return True
    @staticmethod
    def validar(usuario, password_raw):
        if not os.path.exists(ARCHIVO): return False
        with open(ARCHIVO, "r") as f: datos = json.load(f)

        phash = GestorSeguridad().hash_password(password_raw)
        return datos.get(usuario) == phash
