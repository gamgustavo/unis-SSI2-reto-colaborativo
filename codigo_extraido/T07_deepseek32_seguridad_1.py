import base64
import hashlib
import hmac
import json
import pickle
import zlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from cryptography.fernet import Fernet
import secrets
import logging

# Configuración de logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class SecureSessionManager:
    """Gestor seguro de sesiones con cifrado, integridad y validación"""
    
    def __init__(self, secret_key: Optional[str] = None, max_age: int = 3600):
        """
        Inicializa el gestor de sesiones.
        
        Args:
            secret_key: Clave secreta para firmar y cifrar. Si es None, se genera una.
            max_age: Tiempo máximo de vida de la sesión en segundos (por defecto 1 hora).
        """
        if secret_key is None:
            # Generar una clave segura si no se proporciona
            secret_key = secrets.token_urlsafe(32)
        
        # Derivar claves para diferentes propósitos usando HKDF
        self.signing_key = self._derive_key(secret_key, b'signing')
        self.encryption_key = self._derive_key(secret_key, b'encryption')
        
        self.max_age = max_age
        self.fernet = Fernet(self.encryption_key)
        
    def _derive_key(self, secret: str, purpose: bytes) -> bytes:
        """Deriva una clave específica usando HKDF"""
        # Usamos HMAC-SHA256 para derivación de clave simple
        h = hmac.new(secret.encode(), purpose, hashlib.sha256)
        return h.digest()
    
    def _create_signature(self, data: bytes) -> str:
        """Crea una firma HMAC para los datos"""
        h = hmac.new(self.signing_key, data, hashlib.sha256)
        return base64.urlsafe_b64encode(h.digest()).decode()
    
    def _verify_signature(self, data: bytes, signature: str) -> bool:
        """Verifica la firma HMAC de los datos"""
        expected_signature = self._create_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def serialize_session(self, session_data: Dict[str, Any]) -> str:
        """
        Serializa y cifra los datos de sesión de forma segura.
        
        Args:
            session_data: Diccionario con los datos de la sesión.
            
        Returns:
            Cookie de sesión codificada en base64.
            
        Raises:
            ValueError: Si los datos de sesión no son serializables.
        """
        try:
            # Añadir timestamp de creación
            session_data['_created'] = datetime.utcnow().isoformat()
            session_data['_expires'] = (datetime.utcnow() + timedelta(seconds=self.max_age)).isoformat()
            
            # Serializar usando JSON (más seguro que pickle)
            json_data = json.dumps(session_data, separators=(',', ':')).encode('utf-8')
            
            # Comprimir para reducir tamaño
            compressed_data = zlib.compress(json_data, level=6)
            
            # Cifrar los datos
            encrypted_data = self.fernet.encrypt(compressed_data)
            
            # Crear firma
            signature = self._create_signature(encrypted_data)
            
            # Combinar datos cifrados y firma
            combined = encrypted_data + b'.' + signature.encode()
            
            # Codificar en base64 para transporte
            return base64.urlsafe_b64encode(combined).decode()
            
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error serializando sesión: {e}")
            raise ValueError("Los datos de sesión no son serializables") from e
        except Exception as e:
            logger.error(f"Error inesperado serializando sesión: {e}")
            raise
    
    def deserialize_session(self, session_cookie: str) -> Optional[Dict[str, Any]]:
        """
        Reconstruye el objeto de sesión desde una cookie.
        
        Args:
            session_cookie: Cookie de sesión en bytes o string.
            
        Returns:
            Diccionario con los datos de sesión o None si es inválido.
        """
        if not session_cookie:
            return None
            
        try:
            # Decodificar base64
            if isinstance(session_cookie, str):
                cookie_bytes = session_cookie.encode('utf-8')
            else:
                cookie_bytes = session_cookie
                
            decoded = base64.urlsafe_b64decode(cookie_bytes)
            
            # Separar datos cifrados y firma
            if b'.' not in decoded:
                logger.warning("Cookie sin separador de firma")
                return None
                
            encrypted_data, signature = decoded.split(b'.', 1)
            
            # Verificar firma
            if not self._verify_signature(encrypted_data, signature.decode()):
                logger.warning("Firma de cookie inválida")
                return None
            
            # Descifrar datos
            try:
                decrypted_data = self.fernet.decrypt(encrypted_data, ttl=self.max_age)
            except Exception as e:
                logger.warning(f"Cookie expirada o inválida: {e}")
                return None
            
            # Descomprimir
            decompressed_data = zlib.decompress(decrypted_data)
            
            # Deserializar JSON
            session_data = json.loads(decompressed_data.decode('utf-8'))
            
            # Verificar expiración
            if '_expires' in session_data:
                expires = datetime.fromisoformat(session_data['_expires'])
                if datetime.utcnow() > expires:
                    logger.warning("Sesión expirada")
                    return None
            
            # Eliminar metadatos internos
            session_data.pop('_created', None)
            session_data.pop('_expires', None)
            
            return session_data
            
        except (base64.binascii.Error, json.JSONDecodeError, zlib.error) as e:
            logger.warning(f"Error deserializando cookie: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado deserializando sesión: {e}")
            return None
    
    def validate_session_structure(self, session_data: Dict[str, Any]) -> bool:
        """
        Valida la estructura y contenido de los datos de sesión.
        
        Args:
            session_data: Datos de sesión a validar.
            
        Returns:
            True si la sesión es válida, False en caso contrario.
        """
        if not isinstance(session_data, dict):
            return False
        
        # Validar tipos de datos básicos (evitar objetos complejos)
        allowed_types = (str, int, float, bool, type(None), list, dict)
        
        def validate_value(value):
            if isinstance(value, (list, dict)):
                # Validar recursivamente listas y diccionarios
                if isinstance(value, list):
                    return all(validate_item(v) for v in value)
                else:  # dict
                    return all(isinstance(k, str) and validate_item(v) 
                              for k, v in value.items())
            return isinstance(value, allowed_types)
        
        def validate_item(item):
            if isinstance(item, (list, dict)):
                return validate_value(item)
            return isinstance(item, allowed_types[:5])  # Tipos básicos
        
        try:
            for key, value in session_data.items():
                if not isinstance(key, str):
                    return False
                if not validate_item(value):
                    return False
            return True
        except Exception:
            return False


def reconstruct_session_object(session_cookie: Union[str, bytes], 
                              secret_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Función principal para reconstruir el objeto de sesión desde una cookie.
    
    Esta función aplica múltiples capas de seguridad:
    1. Validación de formato y codificación
    2. Verificación de firma HMAC
    3. Descifrado seguro
    4. Validación de expiración
    5. Sanitización de datos
    
    Args:
        session_cookie: Valor de la cookie de sesión en bytes o string.
        secret_key: Clave secreta para verificar la sesión. Debe ser la misma
                   que se usó para crear la cookie.
                   
    Returns:
        Diccionario con los datos de sesión del usuario o None si la cookie
        es inválida, está manipulada o ha expirado.
        
    Example:
        >>> cookie = "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnpkV0lpT2lK..."
        >>> session = reconstruct_session_object(cookie, "mi-clave-secreta")
        >>> print(session.get("user_id"))
    """
    # Validación básica de entrada
    if not session_cookie:
        return None
    
    # Crear gestor de sesiones
    try:
        session_manager = SecureSessionManager(secret_key=secret_key)
    except Exception as e:
        logger.error(f"Error inicializando gestor de sesiones: {e}")
        return None
    
    # Reconstruir sesión
    session_data = session_manager.deserialize_session(session_cookie)
    
    if session_data and session_manager.validate_session_structure(session_data):
        return session_data
    
    return None


# Ejemplo de uso seguro
if __name__ == "__main__":
    # Clave secreta (en producción, obtener de variable de entorno)
    SECRET_KEY = "clave-super-secreta-y-larga-que-debe-ser-segura"
    
    # Crear gestor de sesiones
    manager = SecureSessionManager(secret_key=SECRET_KEY)
    
    # Datos de sesión de ejemplo (sin información sensible)
    example_session = {
        "user_id": 12345,
        "username": "usuario_ejemplo",
        "role": "user",
        "last_login": "2024-01-15T10:30:00",
        "preferences": {"theme": "dark", "language": "es"}
    }
    
    # Serializar sesión
    try:
        cookie = manager.serialize_session(example_session)
        print(f"Cookie generada: {cookie[:50]}...")
        
        # Reconstruir sesión
        reconstructed = reconstruct_session_object(cookie, SECRET_KEY)
        
        if reconstructed:
            print("Sesión reconstruida exitosamente:")
            print(json.dumps(reconstructed, indent=2))
        else:
            print("Error: No se pudo reconstruir la sesión")
            
    except Exception as e:
        print(f"Error: {e}")
