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
    # Permite nombres de host, IPv4 e IPv6
    if len(hostname) > 255:
        return False, "Nombre de host demasiado largo"
    
    # Patrones de validación básicos
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    # Verificar si es una dirección IP válida
    is_ipv4 = re.match(ipv4_pattern, hostname)
    if is_ipv4:
        # Validar rangos de octetos para IPv4
        octets = hostname.split('.')
        for octet in octets:
            if not 0 <= int(octet) <= 255:
                return False, "Dirección IPv4 inválida"
    
    # Si no es IPv4, IPv6 ni un nombre de host válido, rechazar
    elif not re.match(hostname_pattern, hostname) and not re.match(ipv6_pattern, hostname):
        return False, "Formato de host inválido"
    
    try:
        # Determinar sistema operativo
        system = platform.system().lower()
        
        # Construir comando de ping de forma segura
        # Usar shlex.quote() para prevenir inyección de comandos
        safe_hostname = shlex.quote(hostname)
        
        if system == "windows":
            # Windows: 4 paquetes, timeout de 2 segundos
            command = f"ping -n 4 -w 2000 {safe_hostname}"
        else:
            # Linux/Unix/Mac: 4 paquetes, timeout de 2 segundos
            command = f"ping -c 4 -W 2 {safe_hostname}"
        
        # Ejecutar comando con timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10  # Timeout total de 10 segundos
        )
        
        # Analizar resultado
        if system == "windows":
            # En Windows, buscar "TTL=" en la salida
            is_alive = "TTL=" in result.stdout
        else:
            # En Unix/Linux, verificar código de salida
            is_alive = result.returncode == 0
        
        if is_alive:
            return True, f"El host {hostname} responde al ping"
        else:
            return False, f"El host {hostname} no responde al ping"
            
    except subprocess.TimeoutExpired:
        return False, f"Timeout al intentar hacer ping a {hostname}"
    except FileNotFoundError:
        return False, "Comando ping no encontrado en el sistema"
    except Exception as e:
        # Log genérico sin exponer detalles internos
        return False, f"Error al ejecutar ping: {str(e)}"

# Ejemplo de uso (comentado para evitar ejecución automática)
if __name__ == "__main__":
    # Solicitar entrada del usuario de forma segura
    user_input = input("Ingrese el nombre de host o dirección IP: ")
    
    # Ejecutar ping seguro
    is_alive, message = safe_ping(user_input)
    
    # Mostrar resultado
    print(message)
    
    # También se puede usar directamente:
    # resultado = safe_ping("google.com")
    # print(resultado[1])
