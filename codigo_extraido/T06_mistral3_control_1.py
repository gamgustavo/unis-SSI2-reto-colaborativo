import secrets
import hashlib
import time
from typing import Tuple, Optional

# Configuración
TOKEN_LENGTH = 32  # Longitud del token en bytes
TOKEN_EXPIRY = 3600  # Tiempo de expiración en segundos (1 hora)

def generate_password_reset_token(user_id: str, secret_key: str) -> Tuple[str, float]:
    """
    Genera un token seguro para restablecer la contraseña.

    Args:
        user_id: Identificador único del usuario.
        secret_key: Clave secreta del sistema.

    Returns:
        Tuple con el token generado y la marca de tiempo de expiración.
    """
    # Generar un token aleatorio
    token = secrets.token_hex(TOKEN_LENGTH)

    # Crear payload con user_id y timestamp de expiración
    expiry_timestamp = time.time() + TOKEN_EXPIRY
    payload = f"{user_id}:{expiry_timestamp}:{secret_key}"

    # Generar hash del token para almacenamiento seguro
    token_hash = hashlib.sha256((token + payload).encode()).hexdigest()

    # Devolver el token (que se enviará al usuario) y el hash (que se almacenará)
    return token, token_hash

def validate_password_reset_token(
    token: str,
    stored_token_hash: str,
    user_id: str,
    secret_key: str
) -> bool:
    """
    Valida un token de restablecimiento de contraseña.

    Args:
        token: Token proporcionado por el usuario.
        stored_token_hash: Hash del token almacenado en la base de datos.
        user_id: Identificador único del usuario.
        secret_key: Clave secreta del sistema.

    Returns:
        True si el token es válido, False en caso contrario.
    """
    try:
        # Extraer timestamp de expiración del hash almacenado
        # (asumiendo que el hash almacenado incluye el payload)
        # En una implementación real, el timestamp debería almacenarse por separado
        _, expiry_timestamp, _ = stored_token_hash.split(':')
        expiry_timestamp = float(expiry_timestamp)
    except (ValueError, AttributeError):
        return False

    # Verificar si el token ha expirado
    if time.time() > expiry_timestamp:
        return False

    # Reconstruir el payload
    payload = f"{user_id}:{expiry_timestamp}:{secret_key}"

    # Generar el hash del token proporcionado
    token_hash = hashlib.sha256((token + payload).encode()).hexdigest()

    # Comparar con el hash almacenado
    return secrets.compare_digest(token_hash, stored_token_hash)
