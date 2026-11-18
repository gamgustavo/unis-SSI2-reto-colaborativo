import subprocess
import shlex
import platform
import re

def safe_ping(hostname):
    """
    Realiza un ping seguro a un host y verifica si responde.
    
    Args:
        hostname (str): Nombre del host o dirección IP a verificar.
    
    Returns:
        tuple: (bool, str) - (True si el host responde, mensaje descriptivo)
    
    Seguridad:
        - Valida y sanitiza la entrada del usuario
        - Evita inyección de comandos usando shlex.quote()
        - Limita el tiempo de ejecución del comando
        - Usa parámetros específicos por sistema operativo
    """
    
    # Validación de entrada
    if not hostname or not isinstance(hostname, str):
        return False, "Nombre de host inválido"
    
    # Limpiar espacios en blanco
    hostname = hostname.strip()
    
    # Validación básica de formato (no exhaustiva, pero útil)
    # Patrón para nombres de host y direcciones IP básicas
    host_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9.-]{0,253}[a-zA-Z0-9]$'
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not (re.match(host_pattern, hostname) or re.match(ip_pattern, hostname)):
        return False, f"Formato de host inválido: {hostname}"
    
    # Validación adicional para IPs
    if re.match(ip_pattern, hostname):
        parts = hostname.split('.')
        if not all(0 <= int(part) <= 255 for part in parts):
            return False, f"Dirección IP inválida: {hostname}"
    
    # Sanitización: usar shlex.quote para prevenir inyección de comandos
    try:
        safe_hostname = shlex.quote(hostname)
    except ValueError:
        return False, "Nombre de host contiene caracteres no válidos"
    
    # Determinar sistema operativo y construir comando seguro
    system = platform.system().lower()
    
    if system == "windows":
        # Windows: -n número de paquetes, -w timeout
        command = f"ping -n 2 -w 2000 {safe_hostname}"
    else:
        # Unix/Linux/Mac: -c número de paquetes, -W timeout
        command = f"ping -c 2 -W 2 {safe_hostname}"
    
    try:
        # Ejecutar comando con timeout para evitar bloqueos
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,  # Timeout total de 5 segundos
            encoding='utf-8',
            errors='ignore'
        )
        
        # Verificar resultado basado en sistema operativo
        if system == "windows":
            # En Windows, éxito si hay "TTL=" en la salida
            is_alive = "TTL=" in result.stdout.upper()
        else:
            # En Unix, éxito si el código de retorno es 0
            is_alive = result.returncode == 0
        
        if is_alive:
            return True, f"Host {hostname} responde al ping"
        else:
            return False, f"Host {hostname} no responde al ping"
            
    except subprocess.TimeoutExpired:
        return False, f"Timeout al intentar hacer ping a {hostname}"
    except subprocess.CalledProcessError as e:
        return False, f"Error al ejecutar ping: {str(e)}"
    except FileNotFoundError:
        return False, "Comando ping no encontrado en el sistema"
    except Exception as e:
        # Captura genérica para cualquier otro error
        return False, f"Error inesperado: {str(e)}"

# Ejemplo de uso (comentado para evitar ejecución automática)
if __name__ == "__main__":
    # Solicitar entrada del usuario de manera segura
    user_input = input("Ingrese el nombre del host o dirección IP: ")
    
    # Ejecutar ping seguro
    is_alive, message = safe_ping(user_input)
    
    # Mostrar resultado
    print(f"Resultado: {message}")
    print(f"Estado: {'Activo' if is_alive else 'Inactivo'}")
