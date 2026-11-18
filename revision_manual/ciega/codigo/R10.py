import subprocess
import re

def ping_host(host):
    try:
        # Validar que el host no contenga caracteres especiales o comandos maliciosos
        if not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise ValueError("Nombre de host inválido")
        
        # Ejecutar el comando ping (ajusta el número de pings según sea necesario)
        response = subprocess.run(
            ['ping', '-c', '4', host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Verificar si el ping fue exitoso
        if response.returncode == 0:
            return f"El host {host} responde."
        else:
            return f"El host {host} no responde."
    except Exception as e:
        return f"Error: {e}"

# Ejemplo de uso
if __name__ == "__main__":
    host = input("Por favor, introduce el nombre de host: ")
    print(ping_host(host))
