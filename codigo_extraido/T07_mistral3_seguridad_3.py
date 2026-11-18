import json
import base64
import hmac
import hashlib
from typing import Dict, Any, Optional
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
import secrets

# Configuración segura - estas claves deben ser almacenadas de forma segura en variables de entorno
SECRET_KEY = secrets.token_hex(32)  # En producción, usa una clave secreta fuerte y segura
SIGNER_SALT = "session-cookie"  # Sal única para firmar cookies de sesión
SESSION_COOKIE_NAME = "session"
SESSION_TIMEOUT = 3600  # 1 hora en segundos

class SecureSessionSerializer:
    def __init__(self, secret_key: str, salt: str):
        if not secret_key or len(secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        self.serializer = URLSafeSerializer(
            secret_key=secret_key,
            salt=salt,
            serializer=json,
            signer_kwargs={
                'key_derivation': 'hmac',
                'digest_method': hashlib.sha256
            }
        )

    def serialize(self, session_data: Dict[str, Any], expires_in: Optional[int] = None) -> str:
        """Serializa y firma los datos de sesión de forma segura."""
        if not isinstance(session_data, dict):
            raise ValueError("Session data must be a dictionary")

        # Validar contenido de la sesión
        for key, value in session_data.items():
            if not isinstance(key, str):
                raise ValueError("Session keys must be strings")
            if isinstance(value, (dict, list)):
                try:
                    json.dumps(value)  # Validar que sea serializable
                except (TypeError, ValueError):
                    raise ValueError(f"Value for key '{key}' is not JSON serializable")

        return self.serializer.dumps(session_data, expires_in=expires_in)

    def deserialize(self, session_value: bytes) -> Dict[str, Any]:
        """Deserializa y verifica la firma de los datos de sesión."""
        if not session_value:
            raise ValueError("Empty session value")

        try:
            # Convertir bytes a string si es necesario
            session_str = session_value.decode('utf-8') if isinstance(session_value, bytes) else session_value

            # Verificar y deserializar
            data = self.serializer.loads(session_str, max_age=SESSION_TIMEOUT)

            # Validar estructura básica
            if not isinstance(data, dict):
                raise ValueError("Invalid session data structure")

            return data
        except (BadSignature, SignatureExpired) as e:
            # En producción, registrar este evento sin revelar detalles al cliente
            raise ValueError("Invalid or expired session") from e
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError("Malformed session data") from e

def reconstruct_session(session_cookie_value: bytes) -> Dict[str, Any]:
    """
    Reconstruye un objeto de sesión a partir del valor de una cookie de sesión.

    Args:
        session_cookie_value: Valor de la cookie de sesión en bytes

    Returns:
        Diccionario con los datos de sesión

    Raises:
        ValueError: Si la cookie es inválida, está corrupta o ha expirado
    """
    if not session_cookie_value:
        raise ValueError("Session cookie value cannot be empty")

    if len(session_cookie_value) > 4096:  # Límite razonable para cookies
        raise ValueError("Session cookie too large")

    try:
        serializer = SecureSessionSerializer(SECRET_KEY, SIGNER_SALT)
        return serializer.deserialize(session_cookie_value)
    except Exception as e:
        # En producción, registrar el error pero no exponer detalles al cliente
        raise ValueError("Failed to reconstruct session") from e

# Ejemplo de uso seguro:
if __name__ == "__main__":
    # Configuración de ejemplo (en producción usa variables de entorno)
    import os
    SECRET_KEY = os.getenv("SESSION_SECRET_KEY", secrets.token_hex(32))

    # Crear una sesión de ejemplo
    example_session = {
        "user_id": 12345,
        "username": "secure_user",
        "roles": ["user"],
        "last_activity": "2023-01-01T12:00:00Z"
    }

    # Serializar (simular creación de cookie)
    serializer = SecureSessionSerializer(SECRET_KEY, SIGNER_SALT)
    cookie_value = serializer.serialize(example_session, expires_in=SESSION_TIMEOUT)

    # Reconstruir sesión
    try:
        reconstructed = reconstruct_session(cookie_value.encode('utf-8'))
        print("Session reconstructed successfully:", reconstructed)
    except ValueError as e:
        print("Error reconstructing session:", str(e))
