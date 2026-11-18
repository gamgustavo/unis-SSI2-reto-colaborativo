import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

class JWTManager:
    def __init__(self):
        # En producción, usa secretos desde variables de entorno con valores seguros
        self.secret_key = os.environ.get("JWT_SECRET_KEY")
        if not self.secret_key:
            raise ValueError("JWT_SECRET_KEY no está configurada en las variables de entorno")
        
        # Verificar que la clave secreta tenga suficiente longitud
        if len(self.secret_key) < 32:
            raise ValueError("La clave secreta debe tener al menos 32 caracteres para mayor seguridad")
        
        # Algoritmo recomendado por OWASP para JWT
        self.algorithm = "HS256"
        
        # Tiempo de expiración del token (en segundos)
        self.access_token_expire = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE", 3600))  # 1 hora por defecto
        self.refresh_token_expire = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE", 2592000))  # 30 días por defecto

    def _validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Valida que el payload contenga los campos requeridos"""
        required_fields = {"sub", "exp", "iat", "type"}
        return all(field in payload for field in required_fields)

    def create_access_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Crea un token JWT de acceso para un usuario
        
        Args:
            user_id: Identificador único del usuario
            additional_claims: Claims adicionales para incluir en el token
            
        Returns:
            Token JWT firmado
        """
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.access_token_expire)
        
        payload = {
            "sub": user_id,
            "exp": expires,
            "iat": now,
            "type": "access",
            "jti": os.urandom(16).hex()  # ID único del token para prevenir replay attacks
        }
        
        # Agregar claims adicionales si se proporcionan
        if additional_claims:
            # Filtrar claims reservados para evitar conflictos
            reserved_claims = {"sub", "exp", "iat", "nbf", "jti", "aud", "iss", "type"}
            for key, value in additional_claims.items():
                if key not in reserved_claims:
                    payload[key] = value
        
        # Asegurar que el payload sea válido
        if not self._validate_payload(payload):
            raise ValueError("Payload del token inválido")
        
        # Generar el token firmado
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def create_refresh_token(self, user_id: str) -> str:
        """
        Crea un token JWT de refresh para un usuario
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token JWT de refresh firmado
        """
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.refresh_token_expire)
        
        payload = {
            "sub": user_id,
            "exp": expires,
            "iat": now,
            "type": "refresh",
            "jti": os.urandom(16).hex()  # ID único del token
        }
        
        # Generar el token firmado
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            token_type: Tipo de token esperado ("access" o "refresh")
            
        Returns:
            Payload decodificado si el token es válido
            
        Raises:
            InvalidTokenError: Si el token es inválido, expirado o no coincide el tipo
        """
        try:
            # Decodificar y verificar el token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "require": ["exp", "iat", "sub", "type"],  # Requerir claims específicos
                    "verify_exp": True,  # Verificar expiración
                    "verify_iat": True,  # Verificar fecha de emisión
                }
            )
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                raise InvalidTokenError(f"Tipo de token inválido. Esperado: {token_type}")
            
            # Verificar que el token no sea demasiado viejo (opcional, medida de seguridad adicional)
            max_token_age = 7 * 24 * 3600  # 7 días máximo
            iat_time = payload.get("iat")
            if iat_time and (time.time() - iat_time > max_token_age):
                raise InvalidTokenError("Token demasiado viejo")
            
            return payload
            
        except ExpiredSignatureError:
            raise InvalidTokenError("Token expirado")
        except InvalidSignatureError:
            raise InvalidTokenError("Firma del token inválida")
        except Exception as e:
            raise InvalidTokenError(f"Token inválido: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Crea un nuevo token de acceso usando un token de refresh válido
        
        Args:
            refresh_token: Token de refresh válido
            
        Returns:
            Nuevo token de acceso
            
        Raises:
            InvalidTokenError: Si el token de refresh es inválido
        """
        try:
            # Verificar el token de refresh
            payload = self.verify_token(refresh_token, "refresh")
            
            # Crear nuevo token de acceso
            user_id = payload.get("sub")
            if not user_id:
                raise InvalidTokenError("Token de refresh no contiene identificador de usuario")
            
            # Extraer claims adicionales del payload original (excluyendo los reservados)
            reserved_claims = {"sub", "exp", "iat", "nbf", "jti", "aud", "iss", "type"}
            additional_claims = {
                key: value for key, value in payload.items() 
                if key not in reserved_claims
            }
            
            return self.create_access_token(user_id, additional_claims)
            
        except InvalidTokenError:
            raise
        except Exception as e:
            raise InvalidTokenError(f"Error al refrescar token: {str(e)}")

    def invalidate_token(self, token: str, blacklist: set) -> None:
        """
        Invalida un token agregándolo a una lista negra
        
        Nota: En una implementación real, usar una base de datos o cache distribuido
        para la lista negra en lugar de un set en memoria.
        
        Args:
            token: Token a invalidar
            blacklist: Conjunto para almacenar tokens invalidados
        """
        try:
            # Decodificar sin verificar para obtener el jti
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get("jti")
            if jti:
                blacklist.add(jti)
        except Exception:
            pass  # Si no se puede decodificar, no se agrega a la lista negra

    def is_token_blacklisted(self, token: str, blacklist: set) -> bool:
        """
        Verifica si un token está en la lista negra
        
        Args:
            token: Token a verificar
            blacklist: Conjunto con tokens invalidados
            
        Returns:
            True si el token está en la lista negra
        """
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get("jti")
            return jti in blacklist if jti else False
        except Exception:
            return False


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar variable de entorno para pruebas
    os.environ["JWT_SECRET_KEY"] = "mi_clave_secreta_muy_larga_y_segura_de_al_menos_32_caracteres"
    
    # Inicializar el gestor de JWT
    jwt_manager = JWTManager()
    
    # Lista negra en memoria (en producción usar Redis o base de datos)
    token_blacklist = set()
    
    # Crear tokens para un usuario
    user_id = "usuario_123"
    
    # Token de acceso
    access_token = jwt_manager.create_access_token(
        user_id,
        additional_claims={"role": "admin", "email": "usuario@ejemplo.com"}
    )
    print(f"Token de acceso creado: {access_token[:50]}...")
    
    # Token de refresh
    refresh_token = jwt_manager.create_refresh_token(user_id)
    print(f"Token de refresh creado: {refresh_token[:50]}...")
    
    # Verificar token de acceso
    try:
        payload = jwt_manager.verify_token(access_token, "access")
        print(f"Token válido. Usuario: {payload.get('sub')}, Rol: {payload.get('role')}")
    except InvalidTokenError as e:
        print(f"Token inválido: {e}")
    
    # Refrescar token de acceso
    try:
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        print(f"Nuevo token de acceso creado: {new_access_token[:50]}...")
    except InvalidTokenError as e:
        print(f"Error al refrescar: {e}")
    
    # Invalidar un token
    jwt_manager.invalidate_token(access_token, token_blacklist)
    if jwt_manager.is_token_blacklisted(access_token, token_blacklist):
        print("Token invalidado correctamente")
