"""
Nodo B Mejorado - Con intercambio de llaves públicas
Escucha en puerto 5556, envía a puerto 5555
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
    print("NODO B - Iniciando...")
    print("  - Escuchando en: localhost:5556")
    print("  - Enviando a: localhost:5555")
    print("=" * 60)

    # Crear receptor
    receptor = ReceptorPrueba(nombre="Nodo B")

    # Crear ensamblador y obtener llave pública
    ensamblador = EnsambladorRed.obtener_instancia()

    # Primero ensamblar sin llave destino para obtener nuestra llave
    config_temp = ConfigRed(
        host_escucha='localhost',
        puerto_escucha=5556,
        host_destino='localhost',
        puerto_destino=5555
    )
    ensamblador.ensamblar(receptor, config_temp)

    # Guardar nuestra llave pública
    mi_llave = ensamblador.obtener_llave_publica()
    llave_path = os.path.join(os.path.dirname(__file__), 'nodo_b.pub')
    with open(llave_path, 'wb') as f:
        f.write(mi_llave)
    print(f"\n[Nodo B] Llave pública guardada en {llave_path}")

    # Esperar a que Nodo A guarde su llave
    llave_a_path = os.path.join(os.path.dirname(__file__), 'nodo_a.pub')
    print("[Nodo B] Esperando llave pública de Nodo A...")
    while not os.path.exists(llave_a_path):
        time.sleep(0.5)

    # Leer llave de Nodo A
    with open(llave_a_path, 'rb') as f:
        llave_a_bytes = f.read()

    # Importar la llave pública (convertir bytes a objeto RSA)
    from src.Red.Cifrado.seguridad import GestorSeguridad
    gestor_temp = GestorSeguridad()
    llave_a = gestor_temp.importar_publica(llave_a_bytes)
    print("[Nodo B] Llave pública de Nodo A recibida")

    # Reensamblar con la llave correcta
    config = ConfigRed(
        host_escucha='localhost',
        puerto_escucha=5556,
        host_destino='localhost',
        puerto_destino=5555,
        llave_publica_destino=llave_a
    )
    emisor = ensamblador.ensamblar(receptor, config)

    print("\n[Nodo B] Ensamblador configurado correctamente")
    print("[Nodo B] Esperando 3 segundos antes de enviar mensajes...\n")
    time.sleep(3)

    # Enviar mensajes de respuesta
    for i in range(3):
        paquete = PaqueteDTO(
            tipo="respuesta_prueba",
            contenido={"numero": i + 1, "texto": f"Respuesta desde Nodo B - Mensaje {i + 1}"},
            origen="Nodo B",
            destino="Nodo A",
            host="localhost",
            puerto_origen=5556,
            puerto_destino=5555
        )

        print(f"[Nodo B] Enviando respuesta {i + 1}...")
        emisor.enviar_cambio(paquete)
        time.sleep(2)

    # Mantener activo para recibir mensajes
    print("\n[Nodo B] Respuestas enviadas. Esperando mensajes...")
    print("[Nodo B] Presiona Ctrl+C para salir\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[Nodo B] Deteniendo...")
        ensamblador.detener()
        # No eliminar archivos aquí, dejar que Nodo A lo haga
        print("[Nodo B] Detenido correctamente")


if __name__ == "__main__":
    main()
