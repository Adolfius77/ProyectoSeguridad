from chatTCP.src.Bus.ServicioDTO import ServicioDTO
from chatTCP.src.ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO

class EventBus:
    def __init__(self):
        # HASHMAP 1: servicios organizados por evento
        self.servicios_por_evento = {}  # key = tipoEvento, val = [ServicioDTO]

        # HASHMAP 2: lookup directo por llave pública
        self.servicios_por_llave_publica = {}  # key = llave_publica, val = ServicioDTO

        # Emisor (inyectado externamente)
        self.emisor = None

    def set_emisor(self, emisor):
        self.emisor = emisor

    # Registra un servicio a un evento
    def registrar_servicio(self, tipo_evento: str, servicio: ServicioDTO):
        lista = self.servicios_por_evento.setdefault(tipo_evento, [])

        # Evitar duplicados
        for s in lista:
            if s.host == servicio.host and s.puerto == servicio.puerto:
                return

        lista.append(servicio)

        # Registrar en el hashmap por llave pública
        self.servicios_por_llave_publica[servicio.llave_publica] = servicio

    # Eliminar servicio de un evento
    def eliminar_servicio(self, tipo_evento: str, servicio: ServicioDTO):
        lista = self.servicios_por_evento.get(tipo_evento)
        if lista:
            lista[:] = [s for s in lista if s.llave_publica != servicio.llave_publica]

    # Publicar un evento
    def publicar_evento(self, paquete: PaqueteDTO):
        self._normalizar_paquete(paquete)

        # Si es INICIAR_CONEXION solo registrar el servicio
        if paquete.tipo_evento == "INICIAR_CONEXION":
            servicio = ServicioDTO(
                puerto=paquete.puerto_origen,
                host=paquete.host,
                llave_publica=paquete.contenido  # contenido = llave pública
            )

            print(f"[EventBus] Registrando servicio: {servicio}")
            # No se registran eventos aquí, solo el servicio al lookup general
            self.servicios_por_llave_publica[servicio.llave_publica] = servicio
            return

        # Notificar subscriptores
        self.notificar_servicios(paquete)

    # ----------------------------------------
    # Notificar servicios suscritos a un tipoEvento
    # ----------------------------------------
    def notificar_servicios(self, paquete: PaqueteDTO):
        lista = self.servicios_por_evento.get(paquete.tipo_evento)
        if not lista:
            return

        for servicio in lista:
            # Evitar mandar a sí mismo
            if servicio.host == paquete.host and servicio.puerto == paquete.puerto_origen:
                continue

            paquete.host = servicio.host
            paquete.puerto_destino = servicio.puerto

            self.emisor.enviar_cambio(paquete)