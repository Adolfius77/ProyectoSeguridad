import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ModeloChatTCP.ChatTCP.LogicaCliente import LogicaCliente

# Instancia global de la lógica de cliente
logica_cliente = LogicaCliente()

# Callback para mostrar mensajes recibidos en la interfaz
def callback_mensaje(paquete):
    try:
        remitente = getattr(paquete, 'origen', 'Desconocido')
        texto = paquete.contenido.get('mensaje', str(paquete.contenido))
        mostrar_mensaje(remitente, texto)
    except Exception as e:
        mostrar_mensaje('Sistema', f'Error mostrando mensaje: {e}')

logica_cliente.set_callback(callback_mensaje)

def enviar_mensaje():
    """Función que se llama al presionar el botón de enviar."""
    mensaje = entrada_mensaje.get()
    if mensaje.strip():  # Verifica que el mensaje no esté vacío o_o
        logica_cliente.enviar_mensaje(mensaje)
        mostrar_mensaje("Yo", mensaje)
        
        # Limpia el campo de entrada -_-
        entrada_mensaje.delete(0, tk.END)

def mostrar_mensaje(emisor, texto):
    """Agrega un mensaje al área de historial de mensajes."""
    historial_mensajes.config(state=tk.NORMAL)
    historial_mensajes.insert(tk.END, f"[{emisor}]: {texto}\n")
    historial_mensajes.config(state=tk.DISABLED)
    historial_mensajes.see(tk.END)

# Configuración de la ventana uwu
ventana = tk.Tk()
ventana.title("Chat de Mensajes TCP")
ventana.geometry("1200x600")

# Estilo del chat 7u7
style = ttk.Style()
style.configure("TFrame", background="drkcyan")
style.configure("TButton", padding=5, relief="flat", background="#128C7E", foreground="darkgreen")
style.configure("Historial.TLabel", background="powderblue", padding=5, relief="raised") 

# Historial de la conversación ù.ú
marco_historial = ttk.Frame(ventana, padding="5", style="TFrame")
marco_historial.pack(expand=True, fill="both")

#Área de Historial de Mensajes O-O
historial_mensajes = scrolledtext.ScrolledText( #se usa el scrolledtext para ver los mensajes anteriores u.u
    marco_historial, 
    wrap=tk.WORD, 
    state=tk.DISABLED, 
    height=20, 
    font=("Arial", 12),
    background="lightcyan", 
    relief="flat"
)
historial_mensajes.pack(expand=True, fill="both", padx=5, pady=5)

marco_entrada = ttk.Frame(ventana, padding="5")
marco_entrada.pack(fill="x")

#Campo de entrada de mensajes (╬▔皿▔)╯
entrada_mensaje = ttk.Entry(marco_entrada, width=40, font=("Arial", 12))
entrada_mensaje.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 5))

#Esto permite que al presionar Enter también se envía el mensaje :D
entrada_mensaje.bind("<Return>", lambda event=None: enviar_mensaje())

# Botón de Enviar 🦎🔥
boton_enviar = ttk.Button(marco_entrada, text="Enviar", command=enviar_mensaje)
boton_enviar.pack(side=tk.RIGHT)

#Mensaje de bienvenida :C
mostrar_mensaje("Sistema", "¡Bienvenido al Chat!")

#Iniciar el Loop Principal de Tkinter :v
ventana.mainloop()