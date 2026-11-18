import secrets
import hashlib
import time
from typing import Tuple, Optional

# Configuración
TOKEN_LENGTH = 32  # Longitud del token en bytes
TOKEN_EXPIRY = 3600  # Tiempo de expiración en segundos (1 hora)

def generate_password_reset_token(user_id: str) -> Tuple[str, str]:
    """
    Genera un token para restablecer la contraseña de un usuario.

    Args:
        user_id: Identificador único del usuario.

    Returns:
        Tuple con el token en formato hexadecimal y el hash del token almacenable.
    """
    # Generar un token aleatorio
    token = secrets.token_hex(TOKEN_LENGTH)

    # Crear un hash del token para almacenarlo de forma segura
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    # Crear un payload con el user_id y la marca de tiempo
    payload = f"{user_id}:{int(time.time())}"

    # Firmar el payload con el token hash
    signature = hashlib.sha256(f"{payload}:{token_hash}".encode()).hexdigest()

    # Combinar payload y firma para el token final
    final_token = f"{payload}:{signature}"

    return token, final_token

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
    try:
        # Dividir el token en payload y firma
        payload, signature = token.rsplit(':', 1)

        # Verificar que el payload contenga el user_id y la marca de tiempo
        if not payload.startswith(f"{user_id}:"):
            return False

        # Extraer la marca de tiempo
        timestamp = int(payload.split(':')[1])

        # Verificar que el token no haya expirado
        if time.time() - timestamp > TOKEN_EXPIRY:
            return False

        # Verificar la firma
        expected_signature = hashlib.sha256(f"{payload}:{stored_token_hash}".encode()).hexdigest()
        if not secrets.compare_digest(signature, expected_signature):
            return False

        # Verificar que el token proporcionado coincida con el hash almacenado
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if not secrets.compare_digest(token_hash, stored_token_hash):
            return False

        return True
    except (ValueError, IndexError):
        return False
