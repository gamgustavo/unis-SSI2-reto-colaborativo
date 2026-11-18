import subprocess
import re

def ping_host(host):
    try:
        # Validar que el host no contenga caracteres especiales o comandos maliciosos
        if not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise ValueError("Nombre de host inválido")

        # Ejecutar el comando ping
        ping_cmd = ["ping", "-c", "4", host]
        result = subprocess.run(ping_cmd, capture_output=True, text=True)

        # Verificar si el host responde
        if result.returncode == 0:
            return f"El host {host} responde."
        else:
            return f"El host {host} no responde."
    except Exception as e:
        return f"Error al hacer ping al host: {e}"

# Ejemplo de uso
if __name__ == "__main__":
    host = input("Por favor, introduce el nombre de host: ")
    print(ping_host(host))
