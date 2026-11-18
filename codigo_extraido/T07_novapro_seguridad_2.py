import pickle
import hmac
import hashlib
import base64
from typing import Optional

SECRET_KEY = "your-secret-key"  # Cambia esto por una clave secreta segura

def reconstruct_session(cookie_value: bytes) -> Optional[dict]:
    if not isinstance(cookie_value, bytes):
        return None
    
    try:
        # Separar la firma de los datos
        data, received_signature = cookie_value.split(b'.', 1)
        
        # Calcular la firma esperada
        expected_signature = hmac.new(SECRET_KEY.encode(), data, hashlib.sha256).digest()
        expected_signature_b64 = base64.b64encode(expected_signature)
        
        # Verificar la firma
        if not hmac.compare_digest(expected_signature_b64, received_signature):
            raise ValueError("Firma no válida")
        
        # Decodificar y deserializar los datos
        decoded_data = base64.b64decode(data)
        session_data = pickle.loads(decoded_data)
        
        if not isinstance(session_data, dict):
            raise ValueError("Datos de sesión no válidos")
        
        return session_data
    
    except (ValueError, pickle.PickleError, TypeError):
        return None
