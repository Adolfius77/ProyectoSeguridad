import tkinter as tk
from tkinter import scrolledtext, ttk
import datetime


class VentanaChat(tk.Toplevel):
    def __init__(self, parent, usuario_destino, logica_cliente):
        super().__init__(parent)
        self.usuario_destino = usuario_destino
        self.logica_cliente = logica_cliente
        self.title(f"Chat con {usuario_destino.nombre}")
        self.geometry("600x500")

        # Interceptar el evento de cierre para no destruir la app completa
        self.protocol("WM_DELETE_WINDOW", self.cerrar_chat)

        self._configurar_ui()
        self.mostrar_mensaje("Sistema", f"Iniciando chat con {usuario_destino.nombre}...")

    def _configurar_ui(self):
        # Estilos
        style = ttk.Style()
        style.configure("TFrame", background="#ECE5DD")

        # Marco Principal
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(expand=True, fill="both")

        # Historial de Mensajes
        self.historial = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Helvetica", 11),
            bg="#E5DDD5",
            bd=0,
            padx=10,
            pady=10
        )
        self.historial.pack(expand=True, fill="both", padx=10, pady=10)
        self.historial.tag_config("remitente", foreground="#075E54", font=("Helvetica", 11, "bold"))
        self.historial.tag_config("yo", foreground="#128C7E", font=("Helvetica", 11, "bold"), justify="right")

        # Área de entrada
        input_frame = tk.Frame(main_frame, bg="#ECE5DD")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.entrada_mensaje = ttk.Entry(input_frame, font=("Helvetica", 12))
        self.entrada_mensaje.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))
        self.entrada_mensaje.bind("<Return>", lambda e: self.enviar_mensaje())

        btn_enviar = tk.Button(
            input_frame,
            text="Enviar ➤",
            command=self.enviar_mensaje,
            bg="#128C7E",
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=15
        )
        btn_enviar.pack(side=tk.RIGHT)

    def enviar_mensaje(self):
        texto = self.entrada_mensaje.get().strip()
        if texto:
            # Enviar a través de la lógica de red
            self.logica_cliente.enviar_mensaje(texto, destino=self.usuario_destino.nombre)

            # Mostrar en mi propia pantalla
            self.mostrar_mensaje("Yo", texto, es_mio=True)
            self.entrada_mensaje.delete(0, tk.END)

    def mostrar_mensaje(self, emisor, texto, es_mio=False):
        self.historial.config(state=tk.NORMAL)

        timestamp = datetime.datetime.now().strftime("%H:%M")
        tag = "yo" if es_mio else "remitente"
        alineacion = "right" if es_mio else "left"

        header = f"{emisor} [{timestamp}]\n"
        body = f"{texto}\n\n"

        # Insertar con formato
        self.historial.insert(tk.END, header, tag)
        self.historial.insert(tk.END, body, alineacion)

        self.historial.config(state=tk.DISABLED)
        self.historial.see(tk.END)

    def cerrar_chat(self):
        self.destroy()