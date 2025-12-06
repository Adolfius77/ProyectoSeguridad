import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
chat_root = os.path.dirname(os.path.dirname(current_dir))
proyecto_root = os.path.dirname(chat_root)

sys.path.insert(0, proyecto_root)
sys.path.insert(0, chat_root)

from src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente
from src.Presentacion.MVC_ChatTCP.Validaciones import ValidadorUsuario, ValidacionError, GestorIntentosLogin
from src.Presentacion.InfzMenuUsuarios import MenuPrincipal  # Importamos el menú real

gestor_intentos = GestorIntentosLogin(max_intentos=3, espera_segundos=15)


def manejar_respuesta_servidor(paquete):
    """Callback para manejar la respuesta asíncrona del servidor"""
    if paquete.tipo == "LOGIN_OK":
        gestor_intentos.registrar_exito()
        ventana.after(0, lambda: accion_exito(paquete.contenido))

    elif paquete.tipo == "ERROR":
        bloqueado = gestor_intentos.registrar_fallo()
        msg_error = f"Error: {paquete.contenido}"
        if bloqueado:
            msg_error += "\n\n¡Has excedido los intentos! Bloqueo temporal activado."
        ventana.after(0, lambda: messagebox.showerror("Login Fallido", msg_error))


def accion_exito(usuario_nombre):
    messagebox.showinfo("Login Correcto", f"¡Bienvenido {usuario_nombre}!")

    # 1. Destruir ventana de login
    ventana.destroy()

    # 2. Iniciar el Menú Principal
    # Pasamos el control al nuevo bucle principal de tkinter
    app = MenuPrincipal(usuario_nombre)
    app.mainloop()


def validar_login():
    """Valida inputs y estado del bloqueo antes de enviar a red"""
    puede_pasar, mensaje_bloqueo = gestor_intentos.puede_intentar()
    if not puede_pasar:
        messagebox.showerror("Cuenta Bloqueada", mensaje_bloqueo)
        return

    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get()

    try:
        ValidadorUsuario.validar_login(usuario, contrasena)
    except ValidacionError as e:
        messagebox.showerror("Datos Inválidos", str(e))
        return

    try:
        gestor_cliente.set_callback(manejar_respuesta_servidor)
        print(f"Enviando login para: {usuario}")
        gestor_cliente.login(usuario, contrasena)

    except Exception as e:
        messagebox.showerror("Error de Conexión",
                             f"No se pudo conectar: {e}\n\nAsegúrate de ejecutar server_main.py primero.")


# --- Configuración Visual ---
ventana = tk.Tk()
ventana.title("Inicio de Sesión")
ancho_ventana = 800
alto_ventana = 500
x_pos = int((ventana.winfo_screenwidth() / 2) - (ancho_ventana / 2))
y_pos = int((ventana.winfo_screenheight() / 2) - (alto_ventana / 2))
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
ventana.configure(bg="#afbfeb")
ventana.resizable(False, False)

panel_central = tk.Frame(ventana, bg="#ffffff", width=400, height=280)
panel_central.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
panel_central.pack_propagate(False)

tk.Label(ventana, text="Inicio de Sesión", font=("Verdana", 20, "bold"), bg="#afbfeb", fg="#4C4FFF").pack(pady=30)

tk.Label(panel_central, text="Usuario:", font=("Verdana", 12, "bold"), bg="#ffffff").pack(pady=(20, 5))
entry_usuario = tk.Entry(panel_central, bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_usuario.pack(pady=5, padx=50, fill='x')

tk.Label(panel_central, text="Contraseña:", font=("Verdana", 12, "bold"), bg="#ffffff").pack(pady=(15, 5))
entry_contrasena = tk.Entry(panel_central, show="*", bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_contrasena.pack(pady=5, padx=50, fill='x')

btn_login = tk.Button(panel_central, text="Ingresar", command=validar_login, font=("Verdana", 12), bg="#4C4FFF",
                      fg="#ffffff", bd=0, cursor="hand2")
btn_login.pack(pady=(25, 10), ipadx=30)


def abrir_registro(event):
    ventana.destroy()
    ruta_registro = os.path.join(os.path.dirname(__file__), "interfazRegistroUsuario.py")
    subprocess.Popen([sys.executable, ruta_registro])


lbl_registro = tk.Label(panel_central, text="¿No tienes cuenta? Regístrate",
                        fg="#3498DB", bg="white", cursor="hand2", font=("Verdana", 9, "underline"))
lbl_registro.pack(side=tk.BOTTOM, pady=20)
lbl_registro.bind("<Button-1>", abrir_registro)

if __name__ == "__main__":
    ventana.mainloop()