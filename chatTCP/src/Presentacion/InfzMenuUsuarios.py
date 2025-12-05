import tkinter as tk
from tkinter import Frame, Label
from chatTCP.src.Presentacion.ObjetosPresentacion.UsuarioOP import UsuariosOP
from chatTCP.src.Presentacion.Observadores.INotificadorNuevoMensaje import INotificadorNuevoMensaje

class VistaListaUsuarios(tk.Frame, INotificadorNuevoMensaje):
    def __init__(self, parent, lista_usuarios, controlador):
        super().__init__(parent)
        self.parent = parent
        self.lista_usuarios = lista_usuarios
        self.controlador = controlador

        self.config(bg="white")

        # Guarda todos los labels de último mensaje para actualizarlos
        self.labels_mensajes = []

        # Guarda referencias a los widgets de cada usuario para poder actualizarlos
        # Diccionario: {nombre_usuario: {"tarjeta": Frame, "ultimo_label": Label, "badge": Label, "badge_container": Frame}}
        self.widgets_usuarios = {}

        # Detecta cuando la ventana cambia de tamaño
        self.parent.bind("<Configure>", lambda e: self.actualizar_wrap())

        self.render()

    def render(self):
        header = Label(
            self,
            text="Usuarios conectados",
            bg="#128C7E",
            fg="white",
            font=("Arial", 18),
            anchor="w",
            padx=20,
            pady=10
        )
        header.pack(fill="x")

        for usuario in self.lista_usuarios:
            self.crear_tarjeta_usuario(usuario)

    def crear_tarjeta_usuario(self, usuario):
        tarjeta = Frame(self, bg="white", cursor="hand2")
        tarjeta.pack(fill="x", padx=15, pady=8)

        # Crear el callback para esta tarjeta
        click_callback = lambda e, u=usuario: self.controlador_callback(u)

        # Bind click a la tarjeta principal
        tarjeta.bind("<Button-1>", click_callback)

        # Avatar
        avatar = Frame(
            tarjeta, width=50, height=50, bg=usuario.color,
            highlightthickness=0, bd=0, cursor="hand2"
        )
        avatar.pack(side="left", padx=10)
        avatar.pack_propagate(False)
        avatar.bind("<Button-1>", click_callback)

        letra = Label(
            avatar,
            text=usuario.nombre[0].upper(),
            fg="white",
            bg=usuario.color,
            font=("Arial", 18, "bold"),
            cursor="hand2"
        )
        letra.pack(expand=True)
        letra.bind("<Button-1>", click_callback)

        # Texto
        texto = Frame(tarjeta, bg="white", cursor="hand2")
        texto.pack(side="left", fill="x", expand=True)
        texto.bind("<Button-1>", click_callback)

        nombre_label = Label(
            texto,
            text=usuario.nombre,
            bg="white",
            anchor="w",
            font=("Arial", 14, "bold"),
            cursor="hand2"
        )
        nombre_label.pack(fill="x")
        nombre_label.bind("<Button-1>", click_callback)

        ultimo_label = Label(
            texto,
            text=usuario.ultimo_mensaje,
            bg="white",
            anchor="w",
            font=("Arial", 11),
            fg="#555",
            justify="left",
            cursor="hand2"
        )
        ultimo_label.pack(fill="x")
        ultimo_label.bind("<Button-1>", click_callback)

        # Guardar referencia para hacer flex dinámico
        self.labels_mensajes.append(ultimo_label)

        # Badge mensajes (solo se muestra si totalMsjNuevos > 0)
        badge = None
        if usuario.totalMsjNuevos > 0:
            badge = Label(
                tarjeta,
                text=str(usuario.totalMsjNuevos),
                bg="#25D366",
                fg="white",
                font=("Arial", 10, "bold"),
                width=3,
                cursor="hand2"
            )
            badge.pack(side="right", padx=10)
            badge.bind("<Button-1>", click_callback)

        # Guardar referencias para poder actualizar dinámicamente
        self.widgets_usuarios[usuario.nombre] = {
            "tarjeta": tarjeta,
            "ultimo_label": ultimo_label,
            "badge": badge,
            "usuario": usuario
        }

        separator = Frame(self, height=1, bg="#E0E0E0")
        separator.pack(fill="x", padx=10)

    def actualizar_wrap(self):
        nuevo_wrap = self.parent.winfo_width() - 120  # espacio para avatar + padding

        if nuevo_wrap < 50:
            nuevo_wrap = 50

        for lbl in self.labels_mensajes:
            lbl.config(wraplength=nuevo_wrap)

    def actualizar(self, usuario_op: UsuariosOP):
        """
        Implementación de INotificadorNuevoMensaje.
        Actualiza la vista cuando hay un cambio en un usuario (nuevo mensaje).

        Args:
            usuario_op: UsuarioOP con información actualizada
        """
        if usuario_op.nombre not in self.widgets_usuarios:
            return

        widgets = self.widgets_usuarios[usuario_op.nombre]

        # Actualizar el último mensaje
        widgets["ultimo_label"].config(text=usuario_op.ultimo_mensaje)

        # Actualizar el objeto usuario guardado
        widgets["usuario"].ultimo_mensaje = usuario_op.ultimo_mensaje
        widgets["usuario"].totalMsjNuevos = usuario_op.totalMsjNuevos

        # Manejar el badge según el número de mensajes nuevos
        if usuario_op.totalMsjNuevos > 0:
            if widgets["badge"] is None:
                # Crear badge si no existe
                click_callback = lambda e, u=widgets["usuario"]: self.controlador_callback(u)
                badge = Label(
                    widgets["tarjeta"],
                    text=str(usuario_op.totalMsjNuevos),
                    bg="#25D366",
                    fg="white",
                    font=("Arial", 10, "bold"),
                    width=3,
                    cursor="hand2"
                )
                badge.pack(side="right", padx=10)
                badge.bind("<Button-1>", click_callback)
                widgets["badge"] = badge
            else:
                # Actualizar badge existente
                widgets["badge"].config(text=str(usuario_op.totalMsjNuevos))
        else:
            # Ocultar badge si no hay mensajes nuevos
            if widgets["badge"] is not None:
                widgets["badge"].pack_forget()
                widgets["badge"].destroy()
                widgets["badge"] = None

    def controlador_callback(self, usuario):
        """
        Callback que se ejecuta cuando el usuario hace click en una tarjeta.
        Resetea el contador de mensajes nuevos y llama al controlador.
        """
        # Resetear el contador de mensajes nuevos a 0
        if usuario.nombre in self.widgets_usuarios:
            widgets = self.widgets_usuarios[usuario.nombre]

            # Actualizar el objeto usuario
            usuario.totalMsjNuevos = 0
            widgets["usuario"].totalMsjNuevos = 0

            # Ocultar el badge
            if widgets["badge"] is not None:
                widgets["badge"].pack_forget()
                widgets["badge"].destroy()
                widgets["badge"] = None

        # Llamar al controlador
        if self.controlador:
            self.controlador(usuario)


# ------------------------ DEMO ------------------------
def abrir_chat(usuario):
    print(f"Abriendo chat con: {usuario.nombre}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lista de Usuarios")
    root.geometry("750x850")

    usuarios = [
        UsuariosOP("Juan Pérez", "Mensaje MUY largo que debe ajustarse al ancho flexible de la ventana.", "#F54242", 3),
        UsuariosOP("María López", "¿Estás conectado?", "#4287F5", 1),
        UsuariosOP("Carlos Ruiz", "Último mensaje...", "#2ECC71", 0),
        UsuariosOP("Lucía Gómez", "Imagen enviada", "#AF52DE", 5)
    ]

    vista = VistaListaUsuarios(root, usuarios, abrir_chat)
    vista.pack(fill="both", expand=True)

    root.mainloop()
