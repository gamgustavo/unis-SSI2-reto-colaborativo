import os
import secrets
import hashlib
import hmac
import time
from typing import Optional, Tuple
from dataclasses import dataclass

# Configuración segura (en producción, usa variables de entorno o un sistema de configuración seguro)
RESET_TOKEN_SECRET = os.getenv('RESET_TOKEN_SECRET', secrets.token_hex(32))
RESET_TOKEN_EXPIRY_SECONDS = 3600  # 1 hora
RESET_TOKEN_LENGTH = 32  # Longitud del token en bytes (64 caracteres hexadecimales)

@dataclass
class PasswordResetToken:
    token_hash: str
    user_id: str
    expires_at: int
    salt: str

def _generate_secure_token() -> str:
    """Genera un token criptográficamente seguro."""
    return secrets.token_hex(RESET_TOKEN_LENGTH)

def _hash_token(token: str, salt: str) -> str:
    """Genera un hash seguro del token usando HMAC-SHA256."""
    return hmac.new(
        key=RESET_TOKEN_SECRET.encode('utf-8'),
        msg=f"{token}{salt}".encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

def generate_password_reset_token(user_id: str) -> Tuple[str, PasswordResetToken]:
    """
    Genera un token seguro para restablecer la contraseña.

    Args:
        user_id: Identificador único del usuario.

    Returns:
        Tuple con el token en texto plano (para enviar al usuario) y los datos del token para almacenar.
    """
    if not user_id:
        raise ValueError("user_id no puede estar vacío")

    token_plain = _generate_secure_token()
    salt = secrets.token_hex(16)
    token_hash = _hash_token(token_plain, salt)
    expires_at = int(time.time()) + RESET_TOKEN_EXPIRY_SECONDS

    token_data = PasswordResetToken(
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at,
        salt=salt
    )

    return token_plain, token_data

def validate_password_reset_token(token_plain: str, stored_token: PasswordResetToken) -> bool:
    """
    Valida un token de restablecimiento de contraseña.

    Args:
        token_plain: Token en texto plano proporcionado por el usuario.
        stored_token: Datos del token almacenados en la base de datos.

    Returns:
        True si el token es válido, False en caso contrario.
    """
    if not token_plain or not stored_token:
        return False

    # Verificar expiración
    if time.time() > stored_token.expires_at:
        return False

    # Verificar el hash del token
    expected_hash = _hash_token(token_plain, stored_token.salt)
    return hmac.compare_digest(expected_hash, stored_token.token_hash)

# Ejemplo de uso (no forma parte de las funciones principales)
if __name__ == "__main__":
    # Generar token
    user_id = "user123"
    token_plain, token_data = generate_password_reset_token(user_id)
    print(f"Token generado: {token_plain}")
    print(f"Datos para almacenar: {token_data}")

    # Validar token (simulando almacenamiento en base de datos)
    is_valid = validate_password_reset_token(token_plain, token_data)
    print(f"Token válido: {is_valid}")

    # Token inválido (expirado o incorrecto)
    invalid_token = "token_invalido"
    is_valid = validate_password_reset_token(invalid_token, token_data)
    print(f"Token inválido: {is_valid}")
