import tkinter as tk
from tkinter import messagebox
import re
import sys
import os
import subprocess 

# --- AJUSTE DE RUTAS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente

# --- CALLBACK DE RESPUESTA ---
def manejar_respuesta_registro(paquete):
    if paquete.tipo == "REGISTRO_OK":
        def exito():
            messagebox.showinfo("Registro Exitoso", "¡Usuario creado correctamente!\nVolviendo al inicio de sesión...")
            
            # 1. Cerramos la ventana de registro
            ventana_registro.destroy()
            
            # 2. Abrimos la ventana de inicio de sesión
            ruta_login = os.path.join(os.path.dirname(__file__), "interfazInicioSesion.py")
            subprocess.Popen([sys.executable, ruta_login])
            
        ventana_registro.after(0, exito)
        
    elif paquete.tipo == "REGISTRO_FAIL":
        ventana_registro.after(0, lambda: messagebox.showerror("Error", "El usuario ya existe o hubo un error en el servidor."))

# --- VALIDACIONES VISUALES (Igual que antes) ---
def validar_contrasena_fuerte(contrasena):
    if len(contrasena) < 6: return False, "La contraseña debe tener al menos 6 caracteres"
    if not re.search(r'[a-z]', contrasena): return False, "La contraseña debe contener letras minúsculas"
    if not re.search(r'[A-Z]', contrasena): return False, "La contraseña debe contener letras mayúsculas"
    if not re.search(r'[0-9]', contrasena): return False, "La contraseña debe contener números"
    return True, "Contraseña fuerte"

def validar_usuario_valido(usuario):
    if not re.match(r'^[a-zA-Z0-9_-]+$', usuario): return False
    return True

def validar_registro():
    nombre = entry_nombre.get().strip()
    contrasena = entry_contrasena.get()
    contrasena_confirmar = entry_contrasena_confirmar.get()

    if not nombre or not contrasena or not contrasena_confirmar:
        messagebox.showerror("Error", "Por favor, completa todos los campos")
        return

    if nombre.isspace():
        messagebox.showerror("Error", "El usuario no puede contener solo espacios")
        return
        
    if contrasena.isspace() or contrasena_confirmar.isspace():
        messagebox.showerror("Error", "La contraseña no puede contener solo espacios")
        return

    if len(nombre) < 3 or len(nombre) > 20:
        messagebox.showerror("Error", "El usuario debe tener entre 3 y 20 caracteres")
        return

    if not validar_usuario_valido(nombre):
        messagebox.showerror("Error", "El usuario solo puede contener letras, números, guiones y guiones bajos")
        return

    if contrasena != contrasena_confirmar:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return

    es_fuerte, mensaje = validar_contrasena_fuerte(contrasena)
    if not es_fuerte:
        continuar = messagebox.askyesno("Advertencia", f"Contraseña débil: {mensaje}\n\n¿Deseas continuar de todas formas?")
        if not continuar: return

    # --- ENVÍO AL SERVIDOR ---
    try:
        gestor_cliente.set_callback(manejar_respuesta_registro)
        print(f"Enviando registro para: {nombre}")
        gestor_cliente.registrar(nombre, contrasena)
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar: {e}")

# --- INTERFAZ GRÁFICA (Igual que antes) ---
ventana_registro = tk.Tk()
ventana_registro.title("Registro de Usuario")
ancho_ventana = 800
alto_ventana = 500
ancho_pantalla = ventana_registro.winfo_screenwidth()
alto_pantalla = ventana_registro.winfo_screenheight()
ventana_registro.resizable(False, False)
x_pos = int((ancho_pantalla / 2) - (ancho_ventana / 2))
y_pos = int((alto_pantalla / 2) - (alto_ventana / 2))
ventana_registro.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
ventana_registro.configure(bg="#afbfeb")

panel_central = tk.Frame(ventana_registro, bg="#ffffff", width=400, height=300)
panel_central.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

lbl_titulo = tk.Label(ventana_registro, text="Registro de Usuario", font=("Verdana", 20, "bold"), bg="#afbfeb", fg="#4C4FFF")
lbl_titulo.pack(pady=30)

lbl_nombre = tk.Label(panel_central, text="Nombre de Usuario:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_nombre.pack(pady=15, padx=80)

entry_nombre = tk.Entry(panel_central, bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_nombre.pack(pady=5, padx=80)

lbl_contrasena = tk.Label(panel_central, text="Contraseña:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_contrasena.pack(pady=30, padx=80)

entry_contrasena = tk.Entry(panel_central, show="*", bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_contrasena.pack(pady=5, padx=80)

lbl_contrasena_confirmar = tk.Label(panel_central, text="Confirmar Contraseña:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_contrasena_confirmar.pack(pady=15, padx=80)

entry_contrasena_confirmar = tk.Entry(panel_central, show="*", bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
entry_contrasena_confirmar.pack(pady=5, padx=80)

btn_registrar = tk.Button(panel_central, text="Registrar", command=validar_registro, font=("Verdana", 12), bg="#4C4FFF", fg="#ffffff", bd=0, padx=10, pady=5)
btn_registrar.pack(pady=(20, 10))

ventana_registro.mainloop()