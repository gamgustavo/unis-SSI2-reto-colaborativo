import base64
import json
import zlib
from typing import Any, Dict, Optional

def decode_session_cookie(cookie_value: str) -> Dict[str, Any]:
    """
    Reconstruye un objeto de sesión a partir del valor de una cookie de sesión.
    
    Args:
        cookie_value: Valor de la cookie de sesión en formato string (bytes codificados).
    
    Returns:
        Diccionario con los datos de la sesión del usuario.
    
    Raises:
        ValueError: Si la cookie no puede ser decodificada o descomprimida.
    """
    try:
        # Decodificar de base64
        decoded_bytes = base64.b64decode(cookie_value)
        
        # Intentar descomprimir (muchas sesiones usan compresión)
        try:
            decompressed_bytes = zlib.decompress(decoded_bytes)
        except zlib.error:
            # Si falla la descompresión, asumir que no está comprimido
            decompressed_bytes = decoded_bytes
        
        # Decodificar a string y luego a JSON
        session_str = decompressed_bytes.decode('utf-8')
        session_data = json.loads(session_str)
        
        return session_data
        
    except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"No se pudo decodificar la cookie de sesión: {str(e)}")

# Ejemplo de uso:
if __name__ == "__main__":
    # Ejemplo con una cookie de sesión típica (simulada)
    ejemplo_cookie = "eJxVjEEOwiAQRe+StQkzQ2lp4x1qYkKjCQ0M1MTbG6sLt/ve/3+Bi1rqLnkPc4KJYQ9qg8qk2qC2qB1qjzqgjqgT6ow6oy6oK+oGdUe9oD5Qn6gv1DfqB/WL+sMqjf4BsL0qJg=="
    
    try:
        session = decode_session_cookie(ejemplo_cookie)
        print("Sesión reconstruida:")
        print(json.dumps(session, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"Error: {e}")
