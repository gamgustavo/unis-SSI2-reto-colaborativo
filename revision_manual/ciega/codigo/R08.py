import subprocess
import platform

def ping_host(host):
    try:
        if platform.system().lower() == "windows":
            response = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True)
        else:
            response = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)
        
        if response.returncode == 0:
            print(f"El host {host} responde.")
        else:
            print(f"El host {host} no responde.")
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
host = input("Ingrese el nombre del host: ")
ping_host(host)
