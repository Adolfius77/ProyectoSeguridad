import tkinter as tk
from tkinter import messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)

from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuariosOP
from chatTCP.src.Presentacion.chatindividual import VentanaChat
from chatTCP.src.ModeloChatTCP.ChatTCP.LogicaCliente import gestor_cliente

class MenuPrincipal(tk.Tk):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.title(f"ChatTCP - {usuario_actual}")
        self.geometry("450x650")
        self.configure(bg="#f0f2f5")

        self.chats_abiertos = {}
        self.usuarios_op = []

        gestor_cliente.set_callback(self.procesar_paquete_red)
        self._init_ui()
        self.after(1000, gestor_cliente.obtener_usuarios)

    def _init_ui(self):
        header = tk.Frame(self, bg="#008069", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Usuarios en Línea", bg="#008069", fg="white", font=("Arial", 14, "bold")).place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Button(header, text="⟳", command=gestor_cliente.obtener_usuarios, bg="#006d59", fg="white", bd=0).place(relx=0.9, rely=0.5, anchor="center")

        self.canvas = tk.Canvas(self, bg="#f0f2f5", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f2f5")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=430)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")

    def renderizar_lista(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.usuarios_op:
            tk.Label(self.scrollable_frame, text="Sin usuarios conectados", bg="#f0f2f5").pack(pady=20)
            return

        for user in self.usuarios_op:
            if user.nombre == self.usuario_actual: continue

            card = tk.Frame(self.scrollable_frame, bg="white", padx=10, pady=10)
            card.pack(fill="x", pady=2, padx=5)
            card.bind("<Button-1>", lambda e, u=user: self.abrir_chat(u))
            
            # Avatar
            tk.Label(card, text=user.nombre[0].upper(), bg="#128C7E", fg="white", width=4, height=2, font=("Arial", 10, "bold")).pack(side="left", padx=(0, 10))
            
            # Info
            info = tk.Frame(card, bg="white")
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=user.nombre, font=("Arial", 11, "bold"), bg="white", anchor="w").pack(fill="x")
            
            msg_preview = user.ultimo_mensaje[:25] + "..." if len(user.ultimo_mensaje) > 25 else user.ultimo_mensaje
            tk.Label(info, text=msg_preview, font=("Arial", 9), fg="#666", bg="white", anchor="w").pack(fill="x")

            if user.totalMsjNuevos > 0:
                tk.Label(card, text=str(user.totalMsjNuevos), bg="#25D366", fg="white", font=("Arial", 8, "bold"), width=3).pack(side="right")

            # Bind children
            for child in info.winfo_children():
                child.bind("<Button-1>", lambda e, u=user: self.abrir_chat(u))

    def abrir_chat(self, usuario_op):
        usuario_op.totalMsjNuevos = 0
        self.renderizar_lista()

        if usuario_op.nombre in self.chats_abiertos:
            try:
                self.chats_abiertos[usuario_op.nombre].lift()
                return
            except tk.TclError:
                del self.chats_abiertos[usuario_op.nombre]

        ventana = VentanaChat(self, usuario_op, gestor_cliente)
        self.chats_abiertos[usuario_op.nombre] = ventana

    def procesar_paquete_red(self, paquete):
        print(f"[Menu] Recibido: {paquete.tipo}")
        
        if paquete.tipo == "LISTA_USUARIOS":
            nombres = paquete.contenido
            nuevos_ops = []
            mapa_actual = {u.nombre: u for u in self.usuarios_op}
            
            for nombre in nombres:
                if nombre == "Usuarios conectados...": continue
                if nombre in mapa_actual:
                    nuevos_ops.append(mapa_actual[nombre])
                else:
                    nuevos_ops.append(UsuariosOP(nombre, "Disponible", "#128C7E", 0))
            
            self.usuarios_op = nuevos_ops
            self.after(0, self.renderizar_lista)

        elif paquete.tipo == "MENSAJE":
            remitente = paquete.origen
            contenido = paquete.contenido.get("mensaje", "")
            
            if remitente in self.chats_abiertos:
                try:
                    self.chats_abiertos[remitente].mostrar_mensaje(remitente, contenido)
                    return
                except tk.TclError:
                    del self.chats_abiertos[remitente]

            encontrado = False
            for u in self.usuarios_op:
                if u.nombre == remitente:
                    u.totalMsjNuevos += 1
                    u.ultimo_mensaje = contenido
                    encontrado = True
                    break
            
            if not encontrado:
                gestor_cliente.obtener_usuarios()
            
            self.after(0, self.renderizar_lista)

if __name__ == "__main__":
    app = MenuPrincipal("TestUser")
    app.mainloop()