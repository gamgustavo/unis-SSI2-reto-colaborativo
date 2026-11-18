import subprocess
import platform

def ping_host(host):
    try:
        if platform.system().lower() == "windows":
            response = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True)
        else:
            response = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)
        
        if "unreachable" in response.stdout.lower() or "request timed out" in response.stdout.lower():
            return f"El host {host} no responde."
        else:
            return f"El host {host} responde."
    except Exception as e:
        return f"Error al hacer ping al host {host}: {e}"

# Ejemplo de uso
if __name__ == "__main__":
    host = input("Por favor, introduce el nombre del host: ")
    print(ping_host(host))
