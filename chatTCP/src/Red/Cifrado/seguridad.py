import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet


class GestorSeguridad:
    def __init__(self):
        # Generar claves RSA al iniciar
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

    def obtener_publica_bytes(self):
        """Exporta la llave pública a formato PEM (bytes)"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def importar_publica(self, bytes_llave):
        """Importa una llave pública desde bytes"""
        try:
            return serialization.load_pem_public_key(bytes_llave)
        except Exception as e:
            print(f"Error importando llave: {e}")
            return None

    def cifrar(self, mensaje, llave_publica_destino):
        """
        Cifrado Híbrido:
        1. Genera una llave simétrica (Fernet)
        2. Cifra el mensaje con Fernet
        3. Cifra la llave Fernet con RSA
        """
        try:
            # 1. Generar llave simétrica efímera
            key_fernet = Fernet.generate_key()
            f = Fernet(key_fernet)

            # 2. Cifrar el mensaje real (acepta cualquier tamaño)
            if isinstance(mensaje, str):
                mensaje_bytes = mensaje.encode('utf-8')
            else:
                mensaje_bytes = mensaje  # Ya son bytes

            datos_cifrados = f.encrypt(mensaje_bytes)

            # 3. Cifrar la llave simétrica con RSA
            key_fernet_cifrada = llave_publica_destino.encrypt(
                key_fernet,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 4. Concatenar: LlaveCifrada + Separador + MensajeCifrado
            return key_fernet_cifrada + b':::' + datos_cifrados

        except Exception as e:
            print(f"Error al cifrar: {e}")
            raise e

    def desifrar(self, paquete_bytes):
        """Descifrado Híbrido"""
        try:
            # 1. Separar
            partes = paquete_bytes.split(b':::',1)
            if len(partes) != 2:
                return "{Error: Formato corrupto}"

            key_fernet_cifrada = partes[0]
            datos_cifrados = partes[1]

            # 2. Descifrar la llave simétrica con RSA Privada
            key_fernet = self.private_key.decrypt(
                key_fernet_cifrada,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 3. Descifrar el mensaje real con Fernet
            f = Fernet(key_fernet)
            texto_plano = f.decrypt(datos_cifrados).decode('utf-8')

            return texto_plano

        except Exception as e:
            print(f"Error al descifrar: {e}")
            return "{Error de descifrado}"

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()