import tkinter as tk
from tkinter import scrolledtext, ttk
import datetime

class VentanaChat(tk.Toplevel):
    def __init__(self, parent, usuario_destino, logica_cliente):
        super().__init__(parent)
        self.usuario_destino = usuario_destino
        self.logica_cliente = logica_cliente
        self.title(f"Chat con {usuario_destino.nombre}")
        self.geometry("500x450")
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._configurar_ui()

    def _configurar_ui(self):
        # Frame historial
        self.historial = scrolledtext.ScrolledText(self, state='disabled', font=("Arial", 10), wrap=tk.WORD, padx=10, pady=10)
        self.historial.pack(expand=True, fill='both')
        
        self.historial.tag_config('yo', foreground='#0000FF', justify='right')
        self.historial.tag_config('otro', foreground='#008000', justify='left')
        self.historial.tag_config('meta', foreground='#888888', justify='center', font=("Arial", 8))

        # Frame entrada
        frame_input = tk.Frame(self, bg="#eee", pady=5, padx=5)
        frame_input.pack(fill='x')
        
        self.entry = ttk.Entry(frame_input, font=("Arial", 11))
        self.entry.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.entry.bind("<Return>", lambda e: self.enviar())
        
        ttk.Button(frame_input, text="Enviar", command=self.enviar).pack(side='right')

    def enviar(self):
        texto = self.entry.get().strip()
        if not texto: return
        
        self.logica_cliente.enviar_mensaje(texto, destino=self.usuario_destino.nombre)
        self.mostrar_mensaje("Yo", texto, es_mio=True)
        self.entry.delete(0, tk.END)

    def mostrar_mensaje(self, usuario, texto, es_mio=False):
        self.historial.config(state='normal')
        
        hora = datetime.datetime.now().strftime("%H:%M")
        tag = 'yo' if es_mio else 'otro'
        
        header = f"{usuario} [{hora}]\n"
        self.historial.insert(tk.END, header, (tag, 'bold'))
        self.historial.insert(tk.END, texto + "\n\n", tag)
        
        self.historial.see(tk.END)
        self.historial.config(state='disabled')

    def cerrar(self):
        self.destroy()