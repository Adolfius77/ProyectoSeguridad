"""
Script de prueba para dos ensambladores comunicándose entre sí
Ejecuta dos nodos en procesos separados
"""
import sys
import os
import subprocess
import time
import signal

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def main():
    print("\n" + "=" * 70)
    print(" PRUEBA DE COMUNICACIÓN ENTRE DOS ENSAMBLADORES RED")
    print("=" * 70)
    print("\nEste script ejecuta dos nodos en procesos separados:")
    print("  - Nodo A: Escucha en 5555, envía a 5556")
    print("  - Nodo B: Escucha en 5556, envía a 5555")
    print("\nCada nodo enviará 3 mensajes de prueba al otro.")
    print("=" * 70 + "\n")

    # Obtener rutas de los scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nodo_a_path = os.path.join(script_dir, 'test_nodo_a.py')
    nodo_b_path = os.path.join(script_dir, 'test_nodo_b.py')

    # Verificar que los scripts existen
    if not os.path.exists(nodo_a_path):
        print(f"Error: No se encuentra {nodo_a_path}")
        return
    if not os.path.exists(nodo_b_path):
        print(f"Error: No se encuentra {nodo_b_path}")
        return

    # Iniciar procesos
    print("Iniciando procesos...\n")

    try:
        # Iniciar Nodo B primero (para que esté listo para recibir)
        proceso_b = subprocess.Popen(
            [sys.executable, nodo_b_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("✓ Nodo B iniciado (PID: {})".format(proceso_b.pid))
        time.sleep(1)

        # Iniciar Nodo A
        proceso_a = subprocess.Popen(
            [sys.executable, nodo_a_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        print("✓ Nodo A iniciado (PID: {})\n".format(proceso_a.pid))

        print("=" * 70)
        print("PROCESOS EJECUTÁNDOSE - Presiona Ctrl+C para detener")
        print("=" * 70 + "\n")

        # Función para leer salida de un proceso
        def leer_salida(proceso, prefijo):
            while True:
                linea = proceso.stdout.readline()
                if not linea:
                    break
                print(f"{prefijo} {linea.rstrip()}")

        # Monitorear salidas (simplificado - solo espera)
        print("Esperando 15 segundos para completar el intercambio de mensajes...\n")
        time.sleep(15)

        print("\n" + "=" * 70)
        print("DETENIENDO PROCESOS")
        print("=" * 70 + "\n")

        # Terminar procesos
        proceso_a.terminate()
        proceso_b.terminate()

        # Esperar a que terminen
        proceso_a.wait(timeout=5)
        proceso_b.wait(timeout=5)

        print("✓ Nodo A detenido")
        print("✓ Nodo B detenido")

        print("\n" + "=" * 70)
        print("PRUEBA COMPLETADA")
        print("=" * 70)
        print("\nRevisa la salida arriba para verificar que:")
        print("  1. Ambos nodos se iniciaron correctamente")
        print("  2. Los mensajes fueron enviados y recibidos")
        print("  3. El cifrado/descifrado funcionó correctamente")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupción detectada. Deteniendo procesos...")
        try:
            proceso_a.terminate()
            proceso_b.terminate()
            proceso_a.wait(timeout=5)
            proceso_b.wait(timeout=5)
        except:
            proceso_a.kill()
            proceso_b.kill()
        print("Procesos detenidos.\n")

    except Exception as e:
        print(f"\nError durante la ejecución: {e}\n")
        try:
            proceso_a.terminate()
            proceso_b.terminate()
        except:
            pass


if __name__ == "__main__":
    main()
