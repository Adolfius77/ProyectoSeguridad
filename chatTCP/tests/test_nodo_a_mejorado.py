"""
Nodo A Mejorado - Con intercambio de llaves públicas
Escucha en puerto 5555, envía a puerto 5556
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.Red import EnsambladorRed, ConfigRed
from src.ModeloChatTCP.DTOs.PaqueteDTO import PaqueteDTO
from receptor_prueba import ReceptorPrueba


def main():
    print("=" * 60)
    print("NODO A - Iniciando...")
    print("  - Escuchando en: localhost:5555")
    print("  - Enviando a: localhost:5556")
    print("=" * 60)

    # Crear receptor
    receptor = ReceptorPrueba(nombre="Nodo A")

    # Crear ensamblador y obtener llave pública
    ensamblador = EnsambladorRed.obtener_instancia()

    # Primero ensamblar sin llave destino para obtener nuestra llave
    config_temp = ConfigRed(
        host_escucha='localhost',
        puerto_escucha=5555,
        host_destino='localhost',
        puerto_destino=5556
    )
    ensamblador.ensamblar(receptor, config_temp)

    # Guardar nuestra llave pública
    mi_llave = ensamblador.obtener_llave_publica()
    llave_path = os.path.join(os.path.dirname(__file__), 'nodo_a.pub')
    with open(llave_path, 'wb') as f:
        f.write(mi_llave)
    print(f"\n[Nodo A] Llave pública guardada en {llave_path}")

    # Esperar a que Nodo B guarde su llave
    llave_b_path = os.path.join(os.path.dirname(__file__), 'nodo_b.pub')
    print("[Nodo A] Esperando llave pública de Nodo B...")
    while not os.path.exists(llave_b_path):
        time.sleep(0.5)

    # Leer llave de Nodo B
    with open(llave_b_path, 'rb') as f:
        llave_b_bytes = f.read()

    # Importar la llave pública (convertir bytes a objeto RSA)
    from src.Red.Cifrado.seguridad import GestorSeguridad
    gestor_temp = GestorSeguridad()
    llave_b = gestor_temp.importar_publica(llave_b_bytes)
    print("[Nodo A] Llave pública de Nodo B recibida")

    # Reensamblar con la llave correcta
    config = ConfigRed(
        host_escucha='localhost',
        puerto_escucha=5555,
        host_destino='localhost',
        puerto_destino=5556,
        llave_publica_destino=llave_b
    )
    emisor = ensamblador.ensamblar(receptor, config)

    print("\n[Nodo A] Ensamblador configurado correctamente")
    print("[Nodo A] Esperando 2 segundos antes de enviar mensajes...\n")
    time.sleep(2)

    # Enviar mensajes de prueba
    for i in range(3):
        paquete = PaqueteDTO(
            tipo="mensaje_prueba",
            contenido={"numero": i + 1, "texto": f"Hola desde Nodo A - Mensaje {i + 1}"},
            origen="Nodo A",
            destino="Nodo B",
            host="localhost",
            puerto_origen=5555,
            puerto_destino=5556
        )

        print(f"[Nodo A] Enviando mensaje {i + 1}...")
        emisor.enviar_cambio(paquete)
        time.sleep(2)

    # Mantener activo para recibir respuestas
    print("\n[Nodo A] Mensajes enviados. Esperando respuestas...")
    print("[Nodo A] Presiona Ctrl+C para salir\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[Nodo A] Deteniendo...")
        ensamblador.detener()
        # Limpiar archivos de llaves
        try:
            os.remove(llave_path)
            os.remove(llave_b_path)
        except:
            pass
        print("[Nodo A] Detenido correctamente")


if __name__ == "__main__":
    main()
