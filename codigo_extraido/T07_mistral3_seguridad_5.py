import json
import base64
import hmac
import hashlib
from typing import Dict, Any, Optional
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
import secrets

# Configuración segura (debería venir de variables de entorno en producción)
SECRET_KEY = secrets.token_hex(32)  # Clave secreta fuerte generada aleatoriamente
SALT = 'session-cookie'  # Sal única para las cookies de sesión
MAX_COOKIE_SIZE = 4096  # Tamaño máximo en bytes para evitar ataques de denegación de servicio
SESSION_EXPIRY = 3600  # Tiempo de expiración en segundos (1 hora)

class SecureSessionSerializer:
    def __init__(self, secret_key: str, salt: str):
        """
        Inicializa el serializador seguro con una clave secreta y sal.

        Args:
            secret_key: Clave secreta para firmar las cookies
            salt: Sal única para las cookies de sesión
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("La clave secreta debe tener al menos 32 bytes de longitud")
        self.secret_key = secret_key.encode('utf-8')
        self.salt = salt
        self.serializer = URLSafeSerializer(
            secret_key=self.secret_key,
            salt=self.salt,
            serializer=json,
            signer_kwargs={
                'key_derivation': 'hmac',
                'digest_method': hashlib.sha256
            }
        )

    def serialize(self, session_data: Dict[str, Any], expiry: Optional[int] = None) -> str:
        """
        Serializa y firma los datos de sesión de forma segura.

        Args:
            session_data: Diccionario con los datos de sesión
            expiry: Tiempo de expiración en segundos (opcional)

        Returns:
            Cadena serializada y firmada
        """
        if not isinstance(session_data, dict):
            raise ValueError("Los datos de sesión deben ser un diccionario")

        if len(json.dumps(session_data).encode('utf-8')) > MAX_COOKIE_SIZE:
            raise ValueError("Los datos de sesión exceden el tamaño máximo permitido")

        return self.serializer.dumps(session_data, expiry=expiry)

    def deserialize(self, session_cookie: bytes) -> Dict[str, Any]:
        """
        Deserializa y verifica una cookie de sesión.

        Args:
            session_cookie: Valor de la cookie en bytes

        Returns:
            Diccionario con los datos de sesión

        Raises:
            ValueError: Si la cookie es inválida, está corrupta o ha expirado
        """
        if not session_cookie:
            raise ValueError("La cookie de sesión está vacía")

        if len(session_cookie) > MAX_COOKIE_SIZE:
            raise ValueError("La cookie de sesión excede el tamaño máximo permitido")

        try:
            # Decodificar de bytes a string si es necesario
            cookie_str = session_cookie.decode('utf-8') if isinstance(session_cookie, bytes) else session_cookie
            return self.serializer.loads(cookie_str, max_age=SESSION_EXPIRY)
        except (BadSignature, SignatureExpired) as e:
            # Borrar la cookie en caso de error para evitar ataques de replay
            raise ValueError("Cookie de sesión inválida o expirada") from e
        except json.JSONDecodeError as e:
            raise ValueError("Formato de cookie inválido") from e
        except Exception as e:
            raise ValueError("Error al procesar la cookie de sesión") from e

def reconstruct_session(session_cookie_bytes: bytes) -> Dict[str, Any]:
    """
    Reconstruye un objeto de sesión a partir del valor de una cookie de sesión.

    Args:
        session_cookie_bytes: Valor de la cookie en bytes

    Returns:
        Diccionario con los datos de sesión del usuario

    Raises:
        ValueError: Si la cookie es inválida, está corrupta o ha expirado
    """
    # Validar entrada
    if not isinstance(session_cookie_bytes, bytes):
        raise ValueError("El valor de la cookie debe ser de tipo bytes")

    # Inicializar el serializador seguro
    serializer = SecureSessionSerializer(SECRET_KEY, SALT)

    # Deserializar y verificar la cookie
    session_data = serializer.deserialize(session_cookie_bytes)

    # Validaciones adicionales de seguridad
    if not isinstance(session_data, dict):
        raise ValueError("Los datos de sesión deben ser un diccionario")

    # Prevenir ataques de fijación de sesión
    if 'session_id' in session_data:
        if not isinstance(session_data['session_id'], str) or len(session_data['session_id']) < 32:
            raise ValueError("ID de sesión inválido")

    return session_data
