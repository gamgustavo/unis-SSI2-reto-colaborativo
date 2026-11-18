import subprocess
import shlex
import platform
import re
from typing import Optional, Tuple

def safe_ping(hostname: str, timeout: int = 4, count: int = 2) -> Tuple[bool, Optional[str]]:
    """
    Realiza un ping seguro a un host y retorna si responde.
    
    Args:
        hostname: Nombre del host o dirección IP a hacer ping
        timeout: Tiempo máximo de espera en segundos (por defecto 4)
        count: Número de paquetes a enviar (por defecto 2)
    
    Returns:
        Tuple[bool, Optional[str]]: (True si responde, mensaje de error o None)
    
    Seguridad:
        - Valida y sanitiza la entrada
        - Usa parámetros posicionales para evitar inyección de comandos
        - Limita el tiempo de ejecución
        - Valida el formato del hostname
    """
    
    # Validación de entrada básica
    if not hostname or not isinstance(hostname, str):
        return False, "Nombre de host inválido"
    
    # Limpiar espacios en blanco
    hostname = hostname.strip()
    
    # Validación de longitud para evitar argumentos excesivamente largos
    if len(hostname) > 255:
        return False, "Nombre de host demasiado largo"
    
    # Validación básica de formato (evitar caracteres peligrosos)
    # Permitir letras, números, puntos, guiones y dos puntos (para IPv6)
    hostname_pattern = r'^[a-zA-Z0-9\.\-:]+$'
    if not re.match(hostname_pattern, hostname):
        return False, "Nombre de host contiene caracteres inválidos"
    
    # Validación adicional para evitar inyección
    # No permitir caracteres de shell como ;, &, |, $, etc.
    dangerous_chars = [';', '&', '|', '$', '`', '>', '<', '(', ')', '{', '}', '[', ']']
    for char in dangerous_chars:
        if char in hostname:
            return False, f"Nombre de host contiene caracteres peligrosos: {char}"
    
    # Determinar comando según sistema operativo
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows: -n para número de paquetes, -w para timeout en ms
            args = ["ping", "-n", str(count), "-w", str(timeout * 1000), hostname]
        else:
            # Unix/Linux/Mac: -c para número de paquetes, -W para timeout en segundos
            args = ["ping", "-c", str(count), "-W", str(timeout), hostname]
        
        # Ejecutar ping con timeout y capturar salida
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 2,  # Timeout adicional para el proceso completo
            shell=False  # IMPORTANTE: shell=False para evitar inyección
        )
        
        # Verificar resultado
        if result.returncode == 0:
            return True, None
        else:
            # Extraer mensaje de error si existe
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, f"Host no responde: {error_msg[:100]}" if error_msg else "Host no responde"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout excedido"
    except FileNotFoundError:
        return False, "Comando ping no encontrado en el sistema"
    except PermissionError:
        return False, "Permiso denegado para ejecutar ping"
    except Exception as e:
        # No exponer detalles internos en producción
        return False, f"Error al ejecutar ping: Error interno"

def main():
    """
    Función principal para interactuar con el usuario.
    """
    print("=== Verificador de Ping Seguro ===")
    
    # Obtener entrada del usuario
    hostname = input("Ingrese el nombre de host o dirección IP: ")
    
    # Ejecutar ping seguro
    is_alive, error_message = safe_ping(hostname)
    
    # Mostrar resultado
    if is_alive:
        print(f"✓ El host '{hostname}' responde al ping.")
    else:
        print(f"✗ El host '{hostname}' no responde.")
        if error_message:
            print(f"   Detalles: {error_message}")

if __name__ == "__main__":
    main()
