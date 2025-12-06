"""
Punto de entrada principal de la aplicación chatTCP
"""
import sys
import os
import subprocess

def main():
    """
    Función principal de la aplicación
    """
    print("Iniciando chatTCP...")
    
    # Ruta a la interfaz de inicio de sesión
    current_dir = os.path.dirname(os.path.abspath(__file__))
    login_script = os.path.join(current_dir, "Presentacion", "interfazInicioSesion.py")
    
    # Ejecutar la interfaz de login
    try:
        subprocess.run([sys.executable, login_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar la aplicación: {e}")
    except KeyboardInterrupt:
        print("Aplicación detenida por el usuario.")

if __name__ == "__main__":
    main()
