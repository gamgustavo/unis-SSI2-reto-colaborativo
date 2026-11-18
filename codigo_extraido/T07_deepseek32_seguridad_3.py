import base64
import hashlib
import hmac
import json
import pickle
import secrets
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class SessionManager:
    """Gestor seguro de sesiones con protección contra vulnerabilidades comunes"""
    
    def __init__(self, secret_key: Optional[str] = None, 
                 max_age: int = 3600,
                 algorithm: str = 'sha256'):
        """
        Inicializa el gestor de sesiones.
        
        Args:
            secret_key: Clave secreta para firmar las cookies. Si es None, se genera una.
            max_age: Tiempo máximo de vida de la sesión en segundos (por defecto 1 hora).
            algorithm: Algoritmo de hash para la firma (por defecto sha256).
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.max_age = max_age
        self.algorithm = algorithm
        
        # Validar algoritmo
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Algoritmo {algorithm} no disponible")
    
    def _create_signature(self, data: str) -> str:
        """Crea una firma HMAC para los datos"""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            self.algorithm
        ).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verifica la firma HMAC de los datos"""
        expected_signature = self._create_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def _safe_decode(self, cookie_value: bytes) -> Optional[Dict[str, Any]]:
        """
        Decodifica de forma segura el valor de la cookie.
        
        Implementa múltiples capas de seguridad:
        1. Validación de formato
        2. Verificación de firma
        3. Validación de timestamp
        4. Deserialización segura
        """
        try:
            # Decodificar de base64
            decoded = base64.urlsafe_b64decode(cookie_value).decode('utf-8')
            
            # Separar firma y datos
            if '.' not in decoded:
                logger.warning("Formato de cookie inválido: no contiene separador")
                return None
                
            signature, encoded_data = decoded.split('.', 1)
            
            # Verificar firma
            if not self._verify_signature(encoded_data, signature):
                logger.warning("Firma de cookie inválida")
                return None
            
            # Decodificar datos
            data_json = base64.urlsafe_b64decode(encoded_data).decode('utf-8')
            session_data = json.loads(data_json)
            
            # Validar timestamp
            if 'expires' not in session_data:
                logger.warning("Cookie sin timestamp de expiración")
                return None
            
            expires = datetime.fromisoformat(session_data['expires'])
            if datetime.utcnow() > expires:
                logger.warning("Cookie expirada")
                return None
            
            # Validar estructura básica
            if 'data' not in session_data:
                logger.warning("Cookie sin datos de sesión")
                return None
            
            # Limpiar datos expirados
            session_data.pop('expires', None)
            
            return session_data.get('data', {})
            
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            logger.warning(f"Error decodificando cookie: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON de sesión: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.warning(f"Error en estructura de sesión: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado procesando cookie: {e}")
            return None
    
    def _safe_encode(self, session_data: Dict[str, Any]) -> bytes:
        """Codifica de forma segura los datos de sesión"""
        # Añadir timestamp de expiración
        expires = datetime.utcnow() + timedelta(seconds=self.max_age)
        data_to_encode = {
            'data': session_data,
            'expires': expires.isoformat(),
            'created': datetime.utcnow().isoformat()
        }
        
        # Serializar a JSON (más seguro que pickle)
        data_json = json.dumps(data_to_encode, default=str)
        encoded_data = base64.urlsafe_b64encode(data_json.encode()).decode()
        
        # Crear firma
        signature = self._create_signature(encoded_data)
        
        # Combinar y codificar
        combined = f"{signature}.{encoded_data}"
        return base64.urlsafe_b64encode(combined.encode())
    
    def create_session(self, user_data: Dict[str, Any]) -> bytes:
        """
        Crea una nueva cookie de sesión segura.
        
        Args:
            user_data: Datos del usuario a almacenar en la sesión.
            
        Returns:
            Cookie de sesión codificada en bytes.
        """
        # Sanitizar datos de entrada
        sanitized_data = self._sanitize_session_data(user_data)
        
        # Crear cookie
        return self._safe_encode(sanitized_data)
    
    def reconstruct_session(self, cookie_value: bytes) -> Optional[Dict[str, Any]]:
        """
        Reconstruye el objeto de sesión del usuario a partir de una cookie.
        
        Args:
            cookie_value: Valor de la cookie en bytes.
            
        Returns:
            Diccionario con los datos de sesión o None si es inválida.
        """
        return self._safe_decode(cookie_value)
    
    def _sanitize_session_data(self, data: Any) -> Dict[str, Any]:
        """
        Sanitiza los datos de sesión para prevenir inyección.
        
        Args:
            data: Datos a sanitizar.
            
        Returns:
            Datos sanitizados.
        """
        if not isinstance(data, dict):
            return {'value': str(data)}
        
        sanitized = {}
        for key, value in data.items():
            # Validar clave
            if not isinstance(key, str):
                key = str(key)
            
            # Sanitizar valor según tipo
            if isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            elif isinstance(value, (list, tuple)):
                # Sanitizar elementos de listas/tuplas
                sanitized[key] = [
                    self._sanitize_session_data(item) if isinstance(item, dict) 
                    else str(item) for item in value
                ]
            elif isinstance(value, dict):
                # Sanitizar recursivamente diccionarios anidados
                sanitized[key] = self._sanitize_session_data(value)
            else:
                # Convertir otros tipos a string
                sanitized[key] = str(value)
        
        return sanitized
    
    def rotate_key(self) -> None:
        """Rota la clave secreta para mayor seguridad"""
        self.secret_key = secrets.token_urlsafe(32)


def reconstruct_session_from_cookie(cookie_value: bytes, 
                                   secret_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Función principal para reconstruir sesión desde cookie.
    
    Args:
        cookie_value: Valor de la cookie en bytes.
        secret_key: Clave secreta (opcional, se genera una si no se proporciona).
        
    Returns:
        Diccionario con datos de sesión o None si es inválida.
    """
    try:
        # Validar entrada básica
        if not cookie_value or not isinstance(cookie_value, bytes):
            logger.warning("Valor de cookie inválido o vacío")
            return None
        
        # Limitar tamaño máximo para prevenir DoS
        if len(cookie_value) > 4096:  # 4KB máximo
            logger.warning("Cookie demasiado grande")
            return None
        
        # Usar gestor de sesiones
        session_manager = SessionManager(secret_key=secret_key)
        return session_manager.reconstruct_session(cookie_value)
        
    except Exception as e:
        logger.error(f"Error reconstruyendo sesión: {e}")
        return None


# Ejemplo de uso (comentado)
if __name__ == "__main__":
    # Crear una sesión de ejemplo
    manager = SessionManager()
    
    # Datos de usuario de ejemplo
    user_session = {
        "user_id": 12345,
        "username": "usuario_ejemplo",
        "roles": ["user", "editor"],
        "preferences": {"theme": "dark", "language": "es"}
    }
    
    # Crear cookie
    cookie = manager.create_session(user_session)
    print(f"Cookie generada: {cookie[:50]}...")
    
    # Reconstruir sesión
    reconstructed = reconstruct_session_from_cookie(cookie)
    print(f"Sesión reconstruida: {reconstructed}")
    
    # Probar con cookie inválida
    invalid_cookie = b"cookie_invalida"
    invalid_result = reconstruct_session_from_cookie(invalid_cookie)
    print(f"Resultado con cookie inválida: {invalid_result}")
