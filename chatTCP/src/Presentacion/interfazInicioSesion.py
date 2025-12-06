import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess
import logging

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
chat_root = os.path.dirname(os.path.dirname(current_dir))
proyecto_root = os.path.dirname(chat_root)

sys.path.insert(0, proyecto_root)
sys.path.insert(0, chat_root)

from src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente

# --- LOGICA DE RESPUESTA DEL SERVIDOR ---
def manejar_respuesta_login(paquete):
    print(f"[UI Login] Respuesta recibida: {paquete.tipo}")
    if paquete.tipo == "LOGIN_OK":
        usuario = paquete.contenido
        ventana_login.after(0, lambda: abrir_menu_principal(usuario))
    elif paquete.tipo == "ERROR":
        mensaje = paquete.contenido if isinstance(paquete.contenido, str) else "Error al iniciar sesión."
        ventana_login.after(0, lambda: messagebox.showerror("Error de Login", mensaje))

def abrir_menu_principal(usuario):
    ventana_login.destroy()
    ruta_menu = os.path.join(os.path.dirname(__file__), "InfzMenuUsuarios.py")
    subprocess.Popen([sys.executable, ruta_menu, usuario])

def abrir_registro(event=None):
    ventana_login.destroy()
    ruta_registro = os.path.join(os.path.dirname(__file__), "interfazRegistroUsuario.py")
    subprocess.Popen([sys.executable, ruta_registro])

def solicitar_login():
    # --- VALIDACIÓN DE CONEXIÓN ---
    if gestor_cliente.emisor is None:
        messagebox.showerror(
            "Error de Conexión", 
            "El cliente no está conectado al servidor.\n\n"
            "Causas posibles:\n"
            "1. El servidor no está ejecutándose.\n"
            "2. No se encontró 'server_public.pem'.\n\n"
            "Por favor inicia el servidor y reinicia esta ventana."
        )
        return

    # NUEVA VALIDACIÓN DE SOCKET
    if not gestor_cliente.verificar_estado_servidor():
        messagebox.showerror(
            "Error de Conexión",
            "No se puede conectar con el servidor (WinError 10061).\n\n"
            "El servidor rechazó la conexión. Asegúrate de que 'server_main.py' esté ejecutándose."
        )
        return
    # ------------------------------

    nombre = entry_nombre.get().strip()
    contrasena = entry_contrasena.get()

    if not nombre or not contrasena:
        messagebox.showwarning("Datos Incompletos", "Por favor ingresa usuario y contraseña.")
        return

    try:
        gestor_cliente.set_callback(manejar_respuesta_login)
        print(f"[UI] Enviando solicitud de login para: {nombre}")
        gestor_cliente.login(nombre, contrasena)
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"Excepción al enviar: {e}")

# --- INTERFAZ GRÁFICA ---
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión - ChatTCP")
ventana_login.resizable(False, False)

ancho_ventana = 400
alto_ventana = 500
x_pos = int((ventana_login.winfo_screenwidth() / 2) - (ancho_ventana / 2))
y_pos = int((ventana_login.winfo_screenheight() / 2) - (alto_ventana / 2))
ventana_login.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
ventana_login.configure(bg="#afbfeb")

panel_central = tk.Frame(ventana_login, bg="#ffffff", width=350, height=400)
panel_central.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
panel_central.pack_propagate(False)

tk.Label(panel_central, text="Bienvenido", font=("Verdana", 22, "bold"), bg="#ffffff", fg="#4C4FFF").pack(pady=(40, 10))

tk.Label(panel_central, text="Usuario:", font=("Verdana", 10, "bold"), bg="#ffffff").pack(pady=(20,5))
entry_nombre = tk.Entry(panel_central, bg="#f0f0f0", relief="sunken", font=("Verdana", 11))
entry_nombre.pack(pady=5, padx=40, fill='x')

tk.Label(panel_central, text="Contraseña:", font=("Verdana", 10, "bold"), bg="#ffffff").pack(pady=(10,5))
entry_contrasena = tk.Entry(panel_central, show="*", bg="#f0f0f0", relief="sunken", font=("Verdana", 11))
entry_contrasena.pack(pady=5, padx=40, fill='x')

btn_login = tk.Button(panel_central, text="Iniciar Sesión", command=solicitar_login, font=("Verdana", 12), bg="#4C4FFF", fg="#ffffff", cursor="hand2", bd=0)
btn_login.pack(pady=(30, 0), ipadx=30, ipady=2)

lbl_registro = tk.Label(panel_central, text="¿No tienes cuenta? Regístrate", fg="#3498DB", bg="white", cursor="hand2", font=("Verdana", 9, "underline"))
lbl_registro.pack(side=tk.BOTTOM, pady=20)
lbl_registro.bind("<Button-1>", abrir_registro)

if __name__ == "__main__":
    ventana_login.mainloop()