import secrets
import hashlib
import time
from typing import Tuple, Optional

# Configuración
TOKEN_LENGTH = 32  # Longitud del token en bytes
TOKEN_EXPIRATION = 3600  # Tiempo de expiración en segundos (1 hora)

def generate_password_reset_token(user_id: str) -> Tuple[str, str]:
    """
    Genera un token para restablecer la contraseña de un usuario.

    Args:
        user_id: Identificador único del usuario.

    Returns:
        Tuple con el token público (para enviar al usuario) y el token hash (para almacenar en DB).
    """
    # Generar token aleatorio
    token = secrets.token_hex(TOKEN_LENGTH)

    # Crear hash del token + user_id + timestamp para almacenar
    timestamp = str(int(time.time()))
    token_data = f"{token}{user_id}{timestamp}".encode('utf-8')
    token_hash = hashlib.sha256(token_data).hexdigest()

    return token, token_hash

def validate_password_reset_token(user_id: str, token: str, stored_token_hash: str) -> bool:
    """
    Valida un token de restablecimiento de contraseña.

    Args:
        user_id: Identificador único del usuario.
        token: Token proporcionado por el usuario.
        stored_token_hash: Hash del token almacenado en la base de datos.

    Returns:
        True si el token es válido, False en caso contrario.
    """
    # Verificar si el token ha expirado
    try:
        # Extraer timestamp del hash almacenado (asumiendo que es el último componente)
        stored_timestamp = int(stored_token_hash.split('|')[-1]) if '|' in stored_token_hash else 0
        if time.time() - stored_timestamp > TOKEN_EXPIRATION:
            return False
    except (ValueError, IndexError):
        return False

    # Recalcular el hash del token proporcionado
    timestamp = str(int(time.time()))
    token_data = f"{token}{user_id}{timestamp}".encode('utf-8')
    calculated_hash = hashlib.sha256(token_data).hexdigest()

    # Comparar hashes de manera segura (para evitar timing attacks)
    return secrets.compare_digest(calculated_hash, stored_token_hash)

# Versión mejorada con almacenamiento del timestamp en el hash
def generate_password_reset_token_v2(user_id: str) -> Tuple[str, str]:
    """
    Versión mejorada que incluye el timestamp en el hash almacenado.
    """
    token = secrets.token_hex(TOKEN_LENGTH)
    timestamp = str(int(time.time()))
    token_data = f"{token}{user_id}{timestamp}".encode('utf-8')
    token_hash = f"{hashlib.sha256(token_data).hexdigest()}|{timestamp}"
    return token, token_hash

def validate_password_reset_token_v2(user_id: str, token: str, stored_token_hash: str) -> bool:
    """
    Versión mejorada que valida usando el timestamp almacenado en el hash.
    """
    try:
        # Separar el hash y el timestamp
        stored_hash, stored_timestamp = stored_token_hash.rsplit('|', 1)
        stored_timestamp = int(stored_timestamp)

        # Verificar expiración
        if time.time() - stored_timestamp > TOKEN_EXPIRATION:
            return False

        # Recalcular hash con el timestamp original
        token_data = f"{token}{user_id}{stored_timestamp}".encode('utf-8')
        calculated_hash = hashlib.sha256(token_data).hexdigest()

        return secrets.compare_digest(calculated_hash, stored_hash)
    except (ValueError, IndexError):
        return False
