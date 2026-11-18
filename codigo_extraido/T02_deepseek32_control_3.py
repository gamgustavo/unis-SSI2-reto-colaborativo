import subprocess
import platform
import sys

def ping_host(hostname):
    """
    Realiza un ping al host especificado y devuelve si responde o no.
    
    Args:
        hostname (str): Nombre del host o dirección IP a hacer ping.
    
    Returns:
        bool: True si el host responde, False si no responde o hay error.
    """
    # Parámetros según el sistema operativo
    if platform.system().lower() == "windows":
        parameters = ["ping", "-n", "2", "-w", "2000", hostname]
    else:
        parameters = ["ping", "-c", "2", "-W", "2", hostname]
    
    try:
        # Ejecutar el comando ping
        output = subprocess.run(parameters, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               timeout=5)
        
        # Verificar el código de retorno
        if output.returncode == 0:
            return True
        else:
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Timeout al intentar hacer ping a {hostname}")
        return False
    except Exception as e:
        print(f"Error al ejecutar ping: {e}")
        return False

def main():
    """Función principal que solicita el host al usuario."""
    if len(sys.argv) > 1:
        # Si se proporciona como argumento de línea de comandos
        hostname = sys.argv[1]
    else:
        # Solicitar entrada interactiva
        hostname = input("Ingrese el nombre de host o dirección IP: ").strip()
    
    if not hostname:
        print("No se proporcionó un nombre de host.")
        return
    
    print(f"Haciendo ping a {hostname}...")
    
    if ping_host(hostname):
        print(f"✓ El host {hostname} responde al ping.")
    else:
        print(f"✗ El host {hostname} NO responde al ping.")

if __name__ == "__main__":
    main()
