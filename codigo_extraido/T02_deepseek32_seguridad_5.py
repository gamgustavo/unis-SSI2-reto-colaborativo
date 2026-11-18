import subprocess
import shlex
import platform
import re
import sys

def safe_ping(hostname):
    """
    Realiza un ping seguro a un host y verifica si responde.
    
    Args:
        hostname (str): Nombre del host o dirección IP a verificar.
    
    Returns:
        tuple: (bool, str) - (True si el host responde, mensaje descriptivo)
    
    Seguridad implementada:
    1. Validación de entrada contra inyección de comandos
    2. Sanitización del hostname
    3. Uso de parámetros separados en lugar de shell=True
    4. Limitación de caracteres permitidos
    5. Timeout para evitar DoS
    6. Validación de longitud
    """
    
    # Validación de entrada
    if not hostname or not isinstance(hostname, str):
        return False, "Error: El hostname no puede estar vacío y debe ser una cadena de texto."
    
    # Limitar longitud para prevenir ataques de desbordamiento
    if len(hostname) > 255:
        return False, "Error: El hostname es demasiado largo (máximo 255 caracteres)."
    
    # Patrón seguro para validar hostnames y direcciones IP
    # Permite: letras, números, guiones, puntos y corchetes para IPv6
    hostname_pattern = re.compile(r'^[a-zA-Z0-9\.\-\[\]:]+$')
    
    if not hostname_pattern.match(hostname):
        return False, "Error: El hostname contiene caracteres no permitidos."
    
    # Sanitización adicional: eliminar espacios y caracteres de control
    hostname = hostname.strip()
    hostname = re.sub(r'[\x00-\x1F\x7F]', '', hostname)
    
    # Determinar el comando ping según el sistema operativo
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows: -n (número de paquetes), -w (timeout en ms)
            args = ["ping", "-n", "2", "-w", "3000", hostname]
        else:
            # Linux/Unix/Mac: -c (número de paquetes), -W (timeout en segundos)
            args = ["ping", "-c", "2", "-W", "3", hostname]
        
        # Ejecutar ping sin shell=True para prevenir inyección de comandos
        # Usar timeout para evitar que el proceso se quede bloqueado
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,  # Timeout total de 10 segundos
            check=False
        )
        
        # Analizar la salida para determinar si el host responde
        if system == "windows":
            # En Windows, buscar "Respuesta desde" o "Reply from"
            if "respuesta desde" in result.stdout.lower() or "reply from" in result.stdout.lower():
                return True, f"El host {hostname} responde al ping."
            else:
                return False, f"El host {hostname} no responde al ping."
        else:
            # En Unix/Linux, verificar el código de salida y la salida
            if result.returncode == 0:
                return True, f"El host {hostname} responde al ping."
            else:
                return False, f"El host {hostname} no responde al ping."
    
    except subprocess.TimeoutExpired:
        return False, f"Error: Timeout al intentar hacer ping a {hostname}."
    except FileNotFoundError:
        return False, "Error: El comando 'ping' no está disponible en el sistema."
    except PermissionError:
        return False, "Error: Permiso denegado para ejecutar el comando ping."
    except Exception as e:
        # No exponer detalles internos en mensajes de error
        return False, f"Error inesperado al intentar hacer ping."

def main():
    """Función principal para interacción con el usuario."""
    print("=== Verificador de Ping Seguro ===")
    
    # Obtener entrada del usuario
    if len(sys.argv) > 1:
        hostname = sys.argv[1]
    else:
        hostname = input("Ingrese el nombre del host o dirección IP: ")
    
    # Ejecutar ping seguro
    is_alive, message = safe_ping(hostname)
    
    # Mostrar resultado
    print(f"\nResultado: {message}")
    
    # Código de salida para scripts
    sys.exit(0 if is_alive else 1)

if __name__ == "__main__":
    main()
