
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Variables globales para el bloqueo temporal
intentos_fallidos = 0
tiempo_bloqueo = None

#Validaciones
# Validar datos
def validar_login():
    global intentos_fallidos, tiempo_bloqueo
    
    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get()

    # Validar que los campos no estén vacíos
    if not usuario or not contrasena:
        messagebox.showerror("Error", "Por favor, completa todos los campos")
        return

    # Validar espacios en blanco
    if not usuario or usuario.isspace():
        messagebox.showerror("Error", "El usuario no puede estar vacío o contener solo espacios")
        return

    # Bloqueo temporal por varios intentos fallidos
    if tiempo_bloqueo and datetime.now() < tiempo_bloqueo:
        segundos_restantes = int((tiempo_bloqueo - datetime.now()).total_seconds())
        messagebox.showerror("Cuenta Bloqueada", f"Demasiados intentos fallidos. Espera {segundos_restantes} segundos")
        return

    # Prueba de login
    usuario_correcto = "admin"
    contrasena_correcta = "1234"

    if usuario == usuario_correcto and contrasena == contrasena_correcta:
        messagebox.showinfo("Login Correcto", "¡Bienvenido al sistema!")
        intentos_fallidos = 0
        tiempo_bloqueo = None
    else:
        intentos_fallidos += 1
        if intentos_fallidos >= 3:
            tiempo_bloqueo = datetime.now() + timedelta(seconds=30)
            messagebox.showerror("Error", "Usuario o contraseña incorrectos\n\nCuenta bloqueada por 30 segundos")
        else:
            intentos_restantes = 3 - intentos_fallidos
            messagebox.showerror("Error", f"Usuario o contraseña incorrectos\n\nIntentos restantes: {intentos_restantes}")


#Configuración de la ventana 
ventana = tk.Tk()
ventana.title("Inicio de Sesión")
ancho_ventana = 800
alto_ventana = 500
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()
ventana.resizable(False, False) 
x_pos = int((ancho_pantalla / 2) - (ancho_ventana / 2))
y_pos = int((alto_pantalla / 2) - (alto_ventana / 2))
ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
ventana.configure(bg="#afbfeb")  # Color de fondo claro


#Creacion panel central
panel_central = tk.Frame(ventana, bg="#ffffff", width=400, height=300)
panel_central.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#Creación de widgets
lbl_inicioSesion = tk.Label(ventana, text="Inicio de Sesión", font=("Verdana", 20, "bold"), bg="#afbfeb", fg="#4C4FFF")
lbl_inicioSesion.pack(pady=30)

lbl_usuario = tk.Label(panel_central, text="Usuario:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_usuario.pack(pady=15, padx=80) # pady da un espacio vertical

entry_usuario = tk.Entry(panel_central,bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_usuario.pack(pady=5, padx=80)

lbl_contrasena = tk.Label(panel_central, text="Contraseña:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_contrasena.pack(pady=30, padx=80)

entry_contrasena = tk.Entry(panel_central, show="*", bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_contrasena.pack(pady=5, padx=80)

btn_login = tk.Button(panel_central, text="Ingresar", command=validar_login, font=("Verdana", 12), bg="#4C4FFF", fg="#ffffff", bd=0, padx=10, pady=5)
btn_login.pack(pady=(20, 10))

#Funcion para pasar a ventana de registro de usuario
def abrir_registro(event):
    ventana.destroy()
    ruta_registro = os.path.join(os.path.dirname(__file__), "interfazRegistroUsuario.py")
    subprocess.Popen([sys.executable, ruta_registro])

#Creación del link de registro
lbl_registro = tk.Label(panel_central, text="¿No tienes cuenta? Regístrate", fg="#3498DB", bg="white", cursor="hand2", font=("Verdana", 9, "underline"))
lbl_registro.pack(pady=(0, 20))
lbl_registro.bind("<Button-1>", abrir_registro)

ventana.mainloop()
