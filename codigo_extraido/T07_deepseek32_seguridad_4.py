import base64
import hashlib
import hmac
import json
import pickle
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import zlib

class SessionManager:
    """Gestor seguro de sesiones con protección contra manipulaciones"""
    
    def __init__(self, secret_key: str, max_age: int = 3600):
        """
        Inicializa el gestor de sesiones.
        
        Args:
            secret_key: Clave secreta para firmar las cookies
            max_age: Tiempo máximo de vida de la sesión en segundos (por defecto 1 hora)
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("La clave secreta debe tener al menos 32 caracteres")
        
        self.secret_key = secret_key.encode()
        self.max_age = max_age
    
    def _create_signature(self, data: bytes) -> str:
        """Crea un HMAC-SHA256 para verificar la integridad de los datos"""
        return hmac.new(self.secret_key, data, hashlib.sha256).hexdigest()
    
    def _serialize_session(self, session_data: Dict[str, Any]) -> bytes:
        """
        Serializa los datos de sesión de forma segura.
        
        Nota: Usamos JSON en lugar de pickle para evitar RCE.
        """
        # Añadir timestamp de expiración
        session_data['_expires'] = (datetime.utcnow() + timedelta(seconds=self.max_age)).isoformat()
        session_data['_created'] = datetime.utcnow().isoformat()
        
        # Serializar a JSON
        json_data = json.dumps(session_data, separators=(',', ':')).encode('utf-8')
        
        # Comprimir para reducir tamaño (opcional)
        compressed = zlib.compress(json_data)
        
        # Codificar en base64 para almacenamiento seguro en cookie
        encoded = base64.urlsafe_b64encode(compressed)
        
        return encoded
    
    def _deserialize_session(self, encoded_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Deserializa los datos de sesión verificando su integridad.
        
        Returns:
            Diccionario con los datos de sesión o None si la sesión es inválida
        """
        try:
            # Decodificar base64
            decoded = base64.urlsafe_b64decode(encoded_data)
            
            # Descomprimir
            decompressed = zlib.decompress(decoded)
            
            # Cargar JSON
            session_data = json.loads(decompressed.decode('utf-8'))
            
            # Verificar expiración
            expires_str = session_data.get('_expires')
            if expires_str:
                expires = datetime.fromisoformat(expires_str)
                if datetime.utcnow() > expires:
                    return None  # Sesión expirada
            
            # Eliminar metadatos internos antes de devolver
            session_data.pop('_expires', None)
            session_data.pop('_created', None)
            
            return session_data
            
        except (json.JSONDecodeError, zlib.error, base64.binascii.Error, UnicodeDecodeError):
            # Cualquier error en el procesamiento indica datos corruptos o manipulados
            return None
    
    def create_session(self, user_data: Dict[str, Any]) -> bytes:
        """
        Crea una nueva sesión para el usuario.
        
        Args:
            user_data: Datos del usuario a almacenar en la sesión
            
        Returns:
            Cookie de sesión serializada y firmada en bytes
        """
        # Añadir nonce para prevenir ataques de repetición
        session_data = user_data.copy()
        session_data['_nonce'] = secrets.token_hex(16)
        
        # Serializar datos
        serialized = self._serialize_session(session_data)
        
        # Crear firma
        signature = self._create_signature(serialized)
        
        # Combinar datos y firma
        cookie_data = serialized + b'.' + signature.encode()
        
        return cookie_data
    
    def reconstruct_session(self, cookie_value: bytes) -> Optional[Dict[str, Any]]:
        """
        Reconstruye el objeto de sesión a partir del valor de la cookie.
        
        Args:
            cookie_value: Valor de la cookie en bytes
            
        Returns:
            Diccionario con los datos de sesión o None si la sesión es inválida
        """
        try:
            # Separar datos y firma
            if b'.' not in cookie_value:
                return None
            
            data_part, signature_part = cookie_value.rsplit(b'.', 1)
            
            # Verificar firma
            expected_signature = self._create_signature(data_part)
            if not hmac.compare_digest(expected_signature, signature_part.decode()):
                return None  # Firma inválida
            
            # Deserializar datos
            session_data = self._deserialize_session(data_part)
            
            return session_data
            
        except (ValueError, AttributeError):
            return None
    
    def validate_session_structure(self, session_data: Dict[str, Any]) -> bool:
        """
        Valida la estructura de los datos de sesión para prevenir inyección.
        
        Args:
            session_data: Datos de sesión a validar
            
        Returns:
            True si la estructura es válida, False en caso contrario
        """
        if not isinstance(session_data, dict):
            return False
        
        # Validar tipos de datos básicos (prevenir objetos complejos peligrosos)
        allowed_types = (str, int, float, bool, type(None), list, dict)
        
        def validate_value(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    if not isinstance(k, str):
                        return False
                    if not validate_value(v):
                        return False
                return True
            elif isinstance(value, list):
                return all(validate_value(item) for item in value)
            else:
                return isinstance(value, allowed_types[:5])
        
        return validate_value(session_data)


def reconstruct_user_session(cookie_value: bytes, secret_key: str) -> Optional[Dict[str, Any]]:
    """
    Función principal para reconstruir el objeto de sesión del usuario.
    
    Args:
        cookie_value: Valor de la cookie de sesión en bytes
        secret_key: Clave secreta para verificar la firma
        
    Returns:
        Diccionario con los datos de sesión o None si la sesión es inválida
    """
    try:
        # Validar entrada básica
        if not cookie_value or not secret_key:
            return None
        
        # Crear gestor de sesiones
        session_manager = SessionManager(secret_key)
        
        # Reconstruir sesión
        session_data = session_manager.reconstruct_session(cookie_value)
        
        if session_data and session_manager.validate_session_structure(session_data):
            return session_data
        
        return None
        
    except Exception:
        # En producción, considerar logging de la excepción
        return None


# Ejemplo de uso:
if __name__ == "__main__":
    # Clave secreta (en producción, obtener de variables de entorno)
    SECRET_KEY = secrets.token_urlsafe(64)
    
    # Crear sesión de ejemplo
    manager = SessionManager(SECRET_KEY)
    
    user_data = {
        "user_id": 12345,
        "username": "usuario_ejemplo",
        "roles": ["user", "editor"],
        "preferences": {"theme": "dark", "language": "es"}
    }
    
    # Crear cookie
    cookie = manager.create_session(user_data)
    print(f"Cookie creada: {cookie[:50]}...")
    
    # Reconstruir sesión usando la función principal
    reconstructed = reconstruct_user_session(cookie, SECRET_KEY)
    
    if reconstructed:
        print("Sesión reconstruida exitosamente:")
        print(json.dumps(reconstructed, indent=2, ensure_ascii=False))
    else:
        print("Error: No se pudo reconstruir la sesión")
    
    # Prueba con datos manipulados
    manipulated_cookie = cookie[:-10] + b"malicious"
    manipulated_result = reconstruct_user_session(manipulated_cookie, SECRET_KEY)
    print(f"\nPrueba con cookie manipulada: {'Inválida' if not manipulated_result else 'Válida (ERROR)'}")
