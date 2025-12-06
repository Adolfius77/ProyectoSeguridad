import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess

# --- Configuración de rutas (CRÍTICO: HACER ESTO PRIMERO) ---
# Obtener la ruta de la carpeta actual (Presentacion)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Obtener la ruta de la carpeta 'src'
src_dir = os.path.dirname(current_dir)
# Obtener la ruta de la carpeta 'chatTCP'
chat_root = os.path.dirname(src_dir)

# Agregar chatTCP al path para poder hacer 'import src...'
if chat_root not in sys.path:
    sys.path.insert(0, chat_root)

# Ahora sí podemos importar
from src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente
from src.Presentacion.MVC_ChatTCP.Validaciones import ValidadorUsuario, ValidacionError, GestorIntentosLogin
from src.Presentacion.InfzMenuUsuarios import MenuPrincipal

gestor_intentos = GestorIntentosLogin(max_intentos=3, espera_segundos=15)

def manejar_respuesta_servidor(paquete):
    if paquete.tipo == "LOGIN_OK":
        gestor_intentos.registrar_exito()
        ventana.after(0, lambda: accion_exito(paquete.contenido))
    elif paquete.tipo == "ERROR":
        gestor_intentos.registrar_fallo()
        ventana.after(0, lambda: messagebox.showerror("Error", f"{paquete.contenido}"))

def accion_exito(usuario_nombre):
    messagebox.showinfo("Bienvenido", f"Hola {usuario_nombre}")
    ventana.destroy()
    app = MenuPrincipal(usuario_nombre)
    app.mainloop()

def validar_login():
    puede, msg = gestor_intentos.puede_intentar()
    if not puede:
        messagebox.showerror("Bloqueado", msg)
        return

    user = entry_usuario.get().strip()
    pwd = entry_contrasena.get()

    try:
        ValidadorUsuario.validar_login(user, pwd)
        gestor_cliente.set_callback(manejar_respuesta_servidor)
        gestor_cliente.login(user, pwd)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def abrir_registro(event):
    ventana.destroy()
    ruta = os.path.join(os.path.dirname(__file__), "interfazRegistroUsuario.py")
    subprocess.Popen([sys.executable, ruta])

# --- GUI ---
ventana = tk.Tk()
ventana.title("Login ChatTCP")
ventana.geometry("400x500")
ventana.configure(bg="#afbfeb")

frame = tk.Frame(ventana, bg="white", padx=20, pady=20)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Iniciar Sesión", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

tk.Label(frame, text="Usuario:", bg="white").pack(anchor="w")
entry_usuario = tk.Entry(frame, width=30)
entry_usuario.pack(pady=5)

tk.Label(frame, text="Contraseña:", bg="white").pack(anchor="w")
entry_contrasena = tk.Entry(frame, width=30, show="*")
entry_contrasena.pack(pady=5)

tk.Button(frame, text="Ingresar", command=validar_login, bg="#4C4FFF", fg="white", width=20).pack(pady=20)

lbl_reg = tk.Label(frame, text="Crear cuenta nueva", fg="blue", cursor="hand2", bg="white")
lbl_reg.pack()
lbl_reg.bind("<Button-1>", abrir_registro)

if __name__ == "__main__":
    ventana.mainloop()