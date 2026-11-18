import pickle
import base64
from itsdangerous import URLSafeTimedSerializer, BadSignature

def reconstruct_session(cookie_value: bytes, secret_key: str, salt: str = 'session') -> dict:
    """
    Reconstruye un objeto de sesión a partir del valor de una cookie de sesión.

    Args:
        cookie_value: Valor de la cookie de sesión en bytes.
        secret_key: Clave secreta usada para firmar la cookie.
        salt: Sal opcional para el serializador.

    Returns:
        Diccionario con los datos de la sesión.

    Raises:
        BadSignature: Si la firma de la cookie no es válida.
    """
    serializer = URLSafeTimedSerializer(
        secret_key=secret_key,
        salt=salt,
        serializer=pickle,
        signer_kwargs={'digest_method': 'sha256'}
    )

    # Decodificar de bytes a string si es necesario
    if isinstance(cookie_value, bytes):
        cookie_value = cookie_value.decode('utf-8')

    # Reconstruir la sesión
    session_data = serializer.loads(cookie_value)
    return session_data
