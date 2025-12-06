import subprocess
import time
import os
import sys

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(project_root, "chatTCP", "server_main.py")
    client_script = os.path.join(project_root, "chatTCP", "src", "main.py")

    print("=== LANZADOR DE PROYECTO CHATTCP ===")
    
    # 1. Iniciar Servidor
    print("Iniciando Servidor...")
    server_process = subprocess.Popen(
        [sys.executable, server_script],
        cwd=project_root,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print("Esperando a que el servidor esté listo (3 segundos)...")
    time.sleep(3)
    
    # 2. Iniciar Cliente
    print("Iniciando Cliente...")
    client_process = subprocess.Popen(
        [sys.executable, client_script],
        cwd=project_root
    )
    
    print("\nProyecto ejecutándose.")
    print("Cierra la ventana del servidor para detener todo.")
    
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("Deteniendo procesos...")
        server_process.terminate()
        client_process.terminate()

if __name__ == "__main__":
    main()
