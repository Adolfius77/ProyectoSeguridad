import tkinter as tk
from tkinter import messagebox, Label, Frame
import sys
import os

# Ajuste de imports para que funcione desde cualquier ruta
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
        self.title(f"ChatTCP - Conectado como: {usuario_actual}")
        self.geometry("450x700")
        self.configure(bg="#f0f2f5")

        # Diccionario para gestionar ventanas de chat abiertas
        # Key: nombre_usuario, Value: instancia_VentanaChat
        self.chats_abiertos = {}

        # Lista de objetos UsuarioOP
        self.usuarios_op = []

        # Configurar callback global
        gestor_cliente.set_callback(self.procesar_paquete_red)

        self._init_ui()

        # Solicitar lista inicial de usuarios
        self.after(1000, gestor_cliente.obtener_usuarios)

    def _init_ui(self):
        # Header
        header = tk.Frame(self, bg="#008069", height=80)
        header.pack(fill="x")

        lbl_titulo = tk.Label(header, text="Usuarios Conectados", bg="#008069", fg="white",
                              font=("Helvetica", 16, "bold"))
        lbl_titulo.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        btn_refresh = tk.Button(header, text="↻", command=gestor_cliente.obtener_usuarios, bg="#006d59", fg="white",
                                bd=0)
        btn_refresh.place(relx=0.9, rely=0.5, anchor=tk.CENTER)

        # Contenedor scrollable para usuarios
        self.canvas = tk.Canvas(self, bg="#f0f2f5", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f2f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=430)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")

    def renderizar_lista(self):
        # Limpiar lista actual
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for user in self.usuarios_op:
            if user.nombre == self.usuario_actual:
                continue  # No mostrarse a sí mismo

            # Tarjeta de Usuario
            card = tk.Frame(self.scrollable_frame, bg="white", padx=10, pady=10)
            card.pack(fill="x", pady=2, padx=2)

            # Evento click
            card.bind("<Button-1>", lambda e, u=user: self.abrir_chat(u))

            # Avatar (Circulo simulado)
            lbl_avatar = tk.Label(card, text=user.nombre[0].upper(), bg=user.color, fg="white", width=4, height=2,
                                  font=("Arial", 10, "bold"))
            lbl_avatar.pack(side="left", padx=(0, 10))
            lbl_avatar.bind("<Button-1>", lambda e, u=user: self.abrir_chat(u))

            # Info
            info_frame = tk.Frame(card, bg="white")
            info_frame.pack(side="left", fill="x", expand=True)

            lbl_name = tk.Label(info_frame, text=user.nombre, font=("Helvetica", 11, "bold"), bg="white", anchor="w")
            lbl_name.pack(fill="x")
            lbl_name.bind("<Button-1>", lambda e, u=user: self.abrir_chat(u))

            # Badge de mensajes nuevos
            if user.totalMsjNuevos > 0:
                lbl_badge = tk.Label(card, text=str(user.totalMsjNuevos), bg="#25D366", fg="white",
                                     font=("Arial", 9, "bold"), width=3)
                lbl_badge.pack(side="right")

    def abrir_chat(self, usuario_op):
        # Resetear contador de mensajes
        usuario_op.totalMsjNuevos = 0
        self.renderizar_lista()

        # Si ya existe, traer al frente
        if usuario_op.nombre in self.chats_abiertos:
            ventana = self.chats_abiertos[usuario_op.nombre]
            try:
                ventana.lift()
                return
            except tk.TclError:
                # La ventana fue cerrada manualmente
                del self.chats_abiertos[usuario_op.nombre]

        # Crear nueva ventana
        ventana = VentanaChat(self, usuario_op, gestor_cliente)
        self.chats_abiertos[usuario_op.nombre] = ventana

    def procesar_paquete_red(self, paquete):
        """Método central que recibe TODO lo que llega de la red"""
        print(f"[MenuPrincipal] Paquete recibido: {paquete.tipo}")

        if paquete.tipo == "LISTA_USUARIOS":
            # Actualizar lista de usuarios
            nombres_conectados = paquete.contenido
            nuevos_ops = []

            # Mantener estado de usuarios existentes
            mapa_existentes = {u.nombre: u for u in self.usuarios_op}

            for nombre in nombres_conectados:
                if nombre == "Usuarios conectados...": continue  # Ignorar header del server

                if nombre in mapa_existentes:
                    nuevos_ops.append(mapa_existentes[nombre])
                else:
                    # Nuevo usuario
                    nuevos_ops.append(UsuariosOP(nombre, "¡Nuevo usuario!", "#3498db", 0))

            self.usuarios_op = nuevos_ops
            self.after(0, self.renderizar_lista)

        elif paquete.tipo == "MENSAJE":
            # Mensaje recibido
            remitente = paquete.origen
            contenido = paquete.contenido.get("mensaje", "")

            # Verificar si tenemos chat abierto con él
            if remitente in self.chats_abiertos:
                try:
                    self.chats_abiertos[remitente].mostrar_mensaje(remitente, contenido)
                except tk.TclError:
                    del self.chats_abiertos[remitente]  # Ventana estaba cerrada

            # Actualizar notificaciones en la lista principal
            encontrado = False
            for user in self.usuarios_op:
                if user.nombre == remitente:
                    if remitente not in self.chats_abiertos:
                        user.totalMsjNuevos += 1
                    user.ultimo_mensaje = contenido[:20] + "..."
                    encontrado = True
                    break

            if not encontrado:
                # El usuario no estaba en la lista (raro, pedir actualización)
                gestor_cliente.obtener_usuarios()

            self.after(0, self.renderizar_lista)


if __name__ == "__main__":
    # Testeo individual
    app = MenuPrincipal("UsuarioTest")
    app.mainloop()