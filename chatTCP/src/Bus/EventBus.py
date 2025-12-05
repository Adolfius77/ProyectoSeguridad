from chatTCP.src.Bus.ServicioDTO import ServicioDTO
from chatTCP.src.Bus.GeneradorId import GeneradorId
from chatTCP.src.PaqueteDTO.PaqueteDTO import PaqueteDTO

class EventBus:
    def __init__(self):
        # HASHMAP 1: servicios organizados por evento
        self.servicios_por_evento = {}  # key = tipoEvento, val = [ServicioDTO]

        # HASHMAP 2: lookup directo por llave pública
        self.servicios_por_llave_publica = {}  # key = llave_publica, val = ServicioDTO

        # HASHMAP 3: lookup directo por ID
        self.servicios_por_id = {}  # key = id, val = ServicioDTO

        # Generador de IDs (singleton)
        self.generador_id = GeneradorId()

        # Emisor (inyectado externamente)
        self.emisor = None

        # Llave pública propia de este nodo (inyectada externamente)
        self.llave_publica_propia = None

    def set_emisor(self, emisor):
        self.emisor = emisor

    def set_llave_publica_propia(self, llave_publica: bytes):
        """Configura la llave pública de este nodo"""
        self.llave_publica_propia = llave_publica

    # Registrar un servicio a un evento
    def registrar_servicio(self, tipo_evento: str, servicio: ServicioDTO):
        lista = self.servicios_por_evento.setdefault(tipo_evento, [])

        # Evitar duplicados
        for s in lista:
            if s.host == servicio.host and s.puerto == servicio.puerto:
                return

        lista.append(servicio)

        # Registrar en el hashmap por llave pública
        self.servicios_por_llave_publica[servicio.llave_publica] = servicio

        # Registrar en el hashmap por ID
        self.servicios_por_id[servicio.id] = servicio

    # Eliminar un servicio de un evento
    def eliminar_servicio(self, tipo_evento: str, servicio: ServicioDTO):
        lista = self.servicios_por_evento.get(tipo_evento)
        if lista:
            lista[:] = [s for s in lista if s.llave_publica != servicio.llave_publica]

        # Eliminar del hashmap por llave pública
        if servicio.llave_publica in self.servicios_por_llave_publica:
            del self.servicios_por_llave_publica[servicio.llave_publica]

        # Eliminar del hashmap por ID
        if servicio.id in self.servicios_por_id:
            del self.servicios_por_id[servicio.id]

    # Normalizar paquete (poner llave pública si falta)
    def _normalizar_paquete(self, paquete: PaqueteDTO):
        if not paquete.llave_publica_origen and self.llave_publica_propia:
            paquete.llave_publica_origen = self.llave_publica_propia

    # Publicar un evento
    def publicar_evento(self, paquete: PaqueteDTO):
        self._normalizar_paquete(paquete)

        # Caso especial: un nuevo servicio se está registrando
        if paquete.tipo == "INICIAR_CONEXION":
            servicio = ServicioDTO(
                id=self.generador_id.generar(),
                puerto=paquete.puerto_origen,
                host=paquete.host,
                llave_publica=paquete.llave_publica_origen
            )

            lista_eventos = paquete.contenido  # contenido = lista de eventos

            print(f"[EventBus] Servicio registrado: {servicio} con ID={servicio.id}")

            if isinstance(lista_eventos, list):
                for evento in lista_eventos:
                    self.registrar_servicio(evento, servicio)

            return

        # Notificar a los servicios suscritos
        self.notificar_servicios(paquete)

    # Notificar servicios suscritos a un tipo de evento
    def notificar_servicios(self, paquete: PaqueteDTO):
        lista = self.servicios_por_evento.get(paquete.tipo)
        if not lista:
            return

        for servicio in lista:
            # Evitar mandar a sí mismo
            if servicio.host == paquete.host and servicio.puerto == paquete.puerto_origen:
                continue

            # Modificar destino del paquete
            paquete.host = servicio.host
            paquete.puerto_destino = servicio.puerto

            self.emisor.enviar_cambio(paquete)
