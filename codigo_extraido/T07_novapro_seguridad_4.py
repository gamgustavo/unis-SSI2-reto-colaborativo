import base64
import json
import hmac
import hashlib
from typing import Optional, Dict

SECRET_KEY = "your_secret_key_here"  # Cambia esto por una clave secreta segura

def reconstruct_session(cookie_value: bytes) -> Optional[Dict]:
    try:
        # Decodificar la cookie de la sesión
        encoded_session, encoded_signature = cookie_value.split(b':', 1)
        session_data = base64.b64decode(encoded_session)
        signature = base64.b64decode(encoded_signature)
        
        # Verificar la firma HMAC
        expected_signature = hmac.new(SECRET_KEY.encode(), session_data, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Firma HMAC no válida")
        
        # Deserializar los datos de la sesión
        session_object = json.loads(session_data.decode())
        return session_object
    except (ValueError, json.JSONDecodeError, TypeError) as e:
        print(f"Error al reconstruir la sesión: {e}")
        return None
