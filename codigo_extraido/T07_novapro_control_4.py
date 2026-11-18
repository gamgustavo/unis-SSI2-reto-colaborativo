import pickle
from typing import Dict, Any

def reconstruir_sesion(cookie_bytes: bytes) -> Dict[str, Any]:
    """
    Reconstruye el objeto de sesión del usuario a partir de los bytes de la cookie.

    Args:
    cookie_bytes (bytes): Los bytes de la cookie de sesión.

    Returns:
    Dict[str, Any]: El objeto de sesión reconstruido.
    """
    try:
        sesion = pickle.loads(cookie_bytes)
        if isinstance(sesion, dict):
            return sesion
        else:
            raise ValueError("La cookie no contiene un objeto de sesión válido.")
    except pickle.PickleError as e:
        raise ValueError(f"Error al deserializar la cookie: {e}")

# Ejemplo de uso
# cookie_bytes = b'...\x81q\x00}\x94.'  # Supongamos que esta es la cookie en bytes
# sesion_reconstruida = reconstruir_sesion(cookie_bytes)
# print(sesion_reconstruida)
