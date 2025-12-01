
import tkinter as tk
from tkinter import messagebox
import re

#Validaciones
def validar_contrasena_fuerte(contrasena):
    """Verifica si la contraseña es fuerte"""
    if len(contrasena) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    if not re.search(r'[a-z]', contrasena):
        return False, "La contraseña debe contener letras minúsculas"
    if not re.search(r'[A-Z]', contrasena):
        return False, "La contraseña debe contener letras mayúsculas"
    if not re.search(r'[0-9]', contrasena):
        return False, "La contraseña debe contener números"
    return True, "Contraseña fuerte"

def validar_usuario_valido(usuario):
    """Verifica que el usuario tenga caracteres válidos"""
    if not re.match(r'^[a-zA-Z0-9_-]+$', usuario):
        return False
    return True

def validar_registro():
    nombre = entry_nombre.get().strip()
    contrasena = entry_contrasena.get()
    contrasena_confirmar = entry_contrasena_confirmar.get()

    # Validar que los campos no estén vacíos
    if not nombre or not contrasena or not contrasena_confirmar:
        messagebox.showerror("Error", "Por favor, completa todos los campos")
        return

    # Validar espacios en blanco en el usuario
    if nombre.isspace():
        messagebox.showerror("Error", "El usuario no puede contener solo espacios")
        return

    # Validar espacios en blanco en la contraseña
    if contrasena.isspace() or contrasena_confirmar.isspace():
        messagebox.showerror("Error", "La contraseña no puede contener solo espacios")
        return

    # Validar longitud del usuario
    if len(nombre) < 3 or len(nombre) > 20:
        messagebox.showerror("Error", "El usuario debe tener entre 3 y 20 caracteres")
        return

    # Validar caracteres válidos en el usuario
    if not validar_usuario_valido(nombre):
        messagebox.showerror("Error", "El usuario solo puede contener letras, números, guiones y guiones bajos")
        return

    # Validar que las contraseñas coincidan
    if contrasena != contrasena_confirmar:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return

    # Validar longitud mínima de contraseña
    if len(contrasena) < 6:
        messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
        return

    # Validar contraseña fuerte
    es_fuerte, mensaje = validar_contrasena_fuerte(contrasena)
    if not es_fuerte:
        messagebox.showwarning("Advertencia", f"Contraseña débil: {mensaje}\n\n¿Deseas continuar de todas formas?")

    # Si todo es válido, registrar al usuario
    messagebox.showinfo("Registro Exitoso", f"¡Usuario '{nombre}' registrado correctamente!")
    
    # Limpiar campos
    entry_nombre.delete(0, tk.END)
    entry_contrasena.delete(0, tk.END)
    entry_contrasena_confirmar.delete(0, tk.END)

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

#Creacion del panel central
panel_central = tk.Frame(ventana_registro, bg="#ffffff", width=400, height=300)
panel_central.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#Creación de widgets
lbl_titulo = tk.Label(ventana_registro, text="Registro de Usuario", font=("Verdana", 20, "bold"), bg="#afbfeb", fg="#4C4FFF")
lbl_titulo.pack(pady=30)

lbl_nombre = tk.Label(panel_central, text="Nombre de Usuario:", font=("Verdana", 12, "bold"), bg="#ffffff")
lbl_nombre.pack(pady=15, padx=80)

entry_nombre = tk.Entry(panel_central,bg="#f0f0f0", bd=2, relief="sunken", font=("Verdana", 11))
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