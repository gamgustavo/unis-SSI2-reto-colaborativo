import subprocess
import platform

def ping_host(host):
    try:
        # Determinar el comando de ping según el sistema operativo
        if platform.system().lower() == "windows":
            command = ["ping", "-n", "1", host]
        else:
            command = ["ping", "-c", "1", host]
        
        # Ejecutar el comando de ping
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Verificar si el host responde
        if result.returncode == 0:
            print(f"El host {host} responde.")
        else:
            print(f"El host {host} no responde.")
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Solicitar al usuario que ingrese el nombre del host
host = input("Por favor, ingrese el nombre del host: ")
ping_host(host)
