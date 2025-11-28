import json
class PaqueteDTO:
    def __init__(self, tipo,contenido, origen=None, destino=None):
        self.tipo = tipo
        self.contenido = contenido
        self.origen = origen
        self.destino = destino
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return PaqueteDTO(data['tipo'], data['contenido'],data.get('origen'), data.get('destino'))
    