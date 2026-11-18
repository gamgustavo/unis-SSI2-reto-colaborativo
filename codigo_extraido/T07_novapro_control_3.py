import pickle
from typing import Dict, Any

def reconstruir_sesion(cookie_bytes: bytes) -> Dict[str, Any]:
    """
    Reconstruye el objeto de sesión del usuario a partir de los bytes de la cookie de sesión.
    
    Args:
    cookie_bytes (bytes): Valor de la cookie de sesión en bytes.
    
    Returns:
    Dict[str, Any]: Objeto de sesión reconstruido.
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
# cookie_bytes = b'...\x81q\x01}q\x02X\x05\x00\x00\x00user_idq\x03K\x01X\x04\x00\x00\x00nameq\x04X\x05\x00\x00\x00Pedroq\x05u.'
# sesion_reconstruida = reconstruir_sesion(cookie_bytes)
# print(sesion_reconstruida)
