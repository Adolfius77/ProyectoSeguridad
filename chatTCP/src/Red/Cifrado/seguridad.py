import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class GestorSeguridad:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
    
    def obtener_publica_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def importar_publica(self, bytes_llave):
        return serialization.load_pem_public_key(bytes_llave)
    
    def cifrar(self, mensaje,llave_publica_destino):
        max_chunk = 190
        mensaje_bytes = mensaje.encode('utf-8')
        
        if len(mensaje_bytes) < max_chunk:
            return llave_publica_destino.encrypt(
                mensaje_bytes,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
        else:
            raise ValueError("mensaje demasiado largo para cifrado asimetrico puro")
        
    def desifrar(self, mensaje_cifrado):
        try:
            texto = self.private_key.decrypt(
                mensaje_cifrado,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            return texto.decode('utf-8')
        except Exception as e:
            print(f"error al desifrar: {e}")
            return "{error cifrado}"
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()