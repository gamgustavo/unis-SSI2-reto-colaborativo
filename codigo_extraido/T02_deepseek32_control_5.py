import subprocess
import platform
import sys

def ping_host(hostname):
    """
    Realiza un ping al host especificado y devuelve si responde o no.
    
    Args:
        hostname (str): Nombre del host o dirección IP a hacer ping.
    
    Returns:
        bool: True si el host responde, False si no responde.
    """
    # Parámetros según el sistema operativo
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '4'  # Número de paquetes a enviar
    
    # Construir el comando
    command = ['ping', param, count, hostname]
    
    try:
        # Ejecutar el comando ping
        # Redirigir la salida a DEVNULL para silenciarla
        output = subprocess.run(command, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL,
                               timeout=10)
        
        # El código de retorno 0 generalmente indica éxito en ping
        return output.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"Timeout al hacer ping a {hostname}")
        return False
    except Exception as e:
        print(f"Error al ejecutar ping: {e}")
        return False

def main():
    """Función principal para interactuar con el usuario."""
    if len(sys.argv) > 1:
        # Si se proporciona argumento por línea de comandos
        hostname = sys.argv[1]
    else:
        # Solicitar entrada interactiva
        hostname = input("Ingrese el nombre de host o dirección IP: ").strip()
    
    if not hostname:
        print("Error: No se proporcionó un nombre de host.")
        return
    
    print(f"Haciendo ping a {hostname}...")
    
    if ping_host(hostname):
        print(f"✓ El host {hostname} responde al ping.")
    else:
        print(f"✗ El host {hostname} NO responde al ping.")

if __name__ == "__main__":
    main()
