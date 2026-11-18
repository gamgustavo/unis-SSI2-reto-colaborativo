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
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '4'  # Número de paquetes a enviar
    
    try:
        # Ejecutar el comando ping
        output = subprocess.run(
            ['ping', param, count, hostname],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        
        # Verificar el código de retorno
        if output.returncode == 0:
            return True
        else:
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Timeout al hacer ping a {hostname}")
        return False
    except Exception as e:
        print(f"Error al ejecutar ping: {e}")
        return False

def main():
    """Función principal que solicita el host al usuario."""
    if len(sys.argv) > 1:
        hostname = sys.argv[1]
    else:
        hostname = input("Ingrese el nombre de host o dirección IP: ").strip()
    
    if not hostname:
        print("No se proporcionó un hostname.")
        return
    
    print(f"Haciendo ping a {hostname}...")
    
    if ping_host(hostname):
        print(f"✅ El host {hostname} responde al ping.")
    else:
        print(f"❌ El host {hostname} NO responde al ping.")

if __name__ == "__main__":
    main()
