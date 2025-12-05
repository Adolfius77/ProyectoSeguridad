import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CLIENTE - %(levelname)s - %(message)s'
)

# --- Configuración de rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
chat_root = os.path.dirname(os.path.dirname(current_dir))
proyecto_root = os.path.dirname(chat_root)

sys.path.insert(0, proyecto_root)
sys.path.insert(0, chat_root)

from src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente
from src.Presentacion.MVC_ChatTCP.Validaciones import ValidadorUsuario, ValidacionError

# --- LOGICA DE RESPUESTA DEL SERVIDOR ---
def manejar_respuesta_registro(paquete):
    print(f"[UI Registro] Respuesta recibida: {paquete.tipo}")
    if paquete.tipo == "REGISTRO_OK":
        ventana_registro.after(0, accion_registro_exitoso)
    elif paquete.tipo == "REGISTRO_FAIL" or paquete.tipo == "ERROR":
        mensaje = paquete.contenido if isinstance(paquete.contenido, str) else "Error al registrar usuario."
        ventana_registro.after(0, lambda: messagebox.showerror("Error de Registro", mensaje))

def accion_registro_exitoso():
    messagebox.showinfo("Registro Exitoso", "¡Cuenta creada correctamente!\nAhora puedes iniciar sesión.")
    volver_al_login()

def volver_al_login(event=None):
    ventana_registro.destroy()
    ruta_login = os.path.join(os.path.dirname(__file__), "interfazInicioSesion.py")
    subprocess.Popen([sys.executable, ruta_login])

def solicitar_registro():
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
    # ------------------------------

    nombre = entry_nombre.get().strip()
    contrasena = entry_contrasena.get()
    confirmacion = entry_contrasena_confirmar.get()

    try:
        es_fuerte, mensaje_pass = ValidadorUsuario.validar_registro(nombre, contrasena, confirmacion)
        if not es_fuerte:
            confirmar = messagebox.askyesno(
                "Seguridad", 
                f"{mensaje_pass}\n\n¿Deseas registrarte de todos modos?"
            )
            if not confirmar: return

    except ValidacionError as e:
        messagebox.showerror("Datos Inválidos", str(e))
        return

    try:
        gestor_cliente.set_callback(manejar_respuesta_registro)
        print(f"[UI] Enviando solicitud de registro para: {nombre}")
        gestor_cliente.registrar(nombre, contrasena)
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"Excepción al enviar: {e}")

# --- INTERFAZ GRÁFICA ---
ventana_registro = tk.Tk()
ventana_registro.title("Registro de Usuario - ChatTCP")
ventana_registro.resizable(False, False)

ancho_ventana = 800
alto_ventana = 500
x_pos = int((ventana_registro.winfo_screenwidth() / 2) - (ancho_ventana / 2))
y_pos = int((ventana_registro.winfo_screenheight() / 2) - (alto_ventana / 2))
ventana_registro.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
ventana_registro.configure(bg="#afbfeb")

panel_central = tk.Frame(ventana_registro, bg="#ffffff", width=400, height=280)
panel_central.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
panel_central.pack_propagate(False)

tk.Label(ventana_registro, text="Crear Nueva Cuenta", font=("Verdana", 20, "bold"), bg="#afbfeb", fg="#4C4FFF").pack(pady=30)

tk.Label(panel_central, text="Usuario:", font=("Verdana", 10, "bold"), bg="#ffffff").pack(pady=(25,5))
entry_nombre = tk.Entry(panel_central, bg="#f0f0f0", relief="sunken", font=("Verdana", 11))
entry_nombre.pack(pady=5, padx=50, fill='x')

tk.Label(panel_central, text="Contraseña:", font=("Verdana", 10, "bold"), bg="#ffffff").pack(pady=(10,5))
entry_contrasena = tk.Entry(panel_central, show="*", bg="#f0f0f0", relief="sunken", font=("Verdana", 11))
entry_contrasena.pack(pady=5, padx=50, fill='x')

tk.Label(panel_central, text="Confirmar Contraseña:", font=("Verdana", 10, "bold"), bg="#ffffff").pack(pady=(10,5))
entry_contrasena_confirmar = tk.Entry(panel_central, show="*", bg="#f0f0f0", relief="sunken", font=("Verdana", 11))
entry_contrasena_confirmar.pack(pady=5, padx=50, fill='x')

btn_registrar = tk.Button(panel_central, text="Registrarse", command=solicitar_registro, font=("Verdana", 12), bg="#4C4FFF", fg="#ffffff", cursor="hand2", bd=0)
btn_registrar.pack(pady=(20, 0), ipadx=30, ipady=2)

lbl_volver = tk.Label(panel_central, text="¿Ya tienes cuenta? Inicia Sesión", fg="#3498DB", bg="white", cursor="hand2", font=("Verdana", 9, "underline"))
lbl_volver.pack(side=tk.BOTTOM, pady=15)
lbl_volver.bind("<Button-1>", volver_al_login)

ventana_registro.mainloop()