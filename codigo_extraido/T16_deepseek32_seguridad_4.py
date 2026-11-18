import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import secrets
from functools import wraps
from flask import request, jsonify, current_app
import hashlib

class JWTManager:
    def __init__(self):
        self._secret_key = self._load_or_generate_secret_key()
        self._algorithm = 'HS256'
        self._token_expiration = timedelta(hours=1)
        self._refresh_token_expiration = timedelta(days=7)
        self._issuer = 'your-app-name'
        self._audience = 'your-app-users'
        
    def _load_or_generate_secret_key(self) -> str:
        """Carga una clave secreta desde variable de entorno o genera una segura"""
        env_key = os.environ.get('JWT_SECRET_KEY')
        if env_key and len(env_key) >= 32:
            return env_key
        
        # Generar una clave segura si no existe en entorno
        secure_key = secrets.token_urlsafe(64)
        print("ADVERTENCIA: JWT_SECRET_KEY no encontrada en variables de entorno. "
              "Usando clave generada (no adecuada para producción).")
        print(f"Para producción, establece JWT_SECRET_KEY={secure_key}")
        return secure_key
    
    def _generate_jti(self) -> str:
        """Genera un identificador único seguro para el token (JWT ID)"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Crea un token JWT de acceso seguro
        
        Args:
            user_id: Identificador único del usuario
            additional_claims: Claims adicionales a incluir en el token
            
        Returns:
            Token JWT firmado
        """
        now = datetime.utcnow()
        payload = {
            'sub': user_id,
            'iat': now,
            'exp': now + self._token_expiration,
            'jti': self._generate_jti(),
            'iss': self._issuer,
            'aud': self._audience,
            'type': 'access'
        }
        
        # Añadir claims adicionales si existen
        if additional_claims:
            # Filtrar claims reservados
            reserved_claims = {'sub', 'iat', 'exp', 'jti', 'iss', 'aud', 'nbf', 'type'}
            for key, value in additional_claims.items():
                if key not in reserved_claims:
                    payload[key] = value
        
        # Firmar el token
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Crea un token de refresco seguro
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token de refresco JWT
        """
        now = datetime.utcnow()
        payload = {
            'sub': user_id,
            'iat': now,
            'exp': now + self._refresh_token_expiration,
            'jti': self._generate_jti(),
            'iss': self._issuer,
            'aud': self._audience,
            'type': 'refresh'
        }
        
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token
    
    def verify_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            token_type: Tipo de token esperado ('access' o 'refresh')
            
        Returns:
            Payload decodificado si la verificación es exitosa
            
        Raises:
            InvalidTokenError: Si el token es inválido
            ExpiredSignatureError: Si el token ha expirado
        """
        try:
            # Decodificar y verificar el token
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={'require': ['exp', 'iat', 'sub', 'jti', 'iss', 'aud']}
            )
            
            # Verificar tipo de token
            if payload.get('type') != token_type:
                raise InvalidTokenError(f"Tipo de token inválido. Esperado: {token_type}")
            
            # Verificar que el token no sea demasiado viejo (opcional)
            iat = datetime.fromtimestamp(payload['iat'])
            max_age = timedelta(days=30)  # Máximo 30 días de antigüedad
            if datetime.utcnow() - iat > max_age:
                raise InvalidTokenError("Token demasiado antiguo")
            
            return payload
            
        except ExpiredSignatureError:
            raise ExpiredSignatureError("Token ha expirado")
        except jwt.InvalidIssuerError:
            raise InvalidTokenError("Emisor del token inválido")
        except jwt.InvalidAudienceError:
            raise InvalidTokenError("Audiencia del token inválida")
        except Exception as e:
            raise InvalidTokenError(f"Token inválido: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresca un token de acceso usando un token de refresco válido
        
        Args:
            refresh_token: Token de refresco válido
            
        Returns:
            Nuevo token de acceso
            
        Raises:
            InvalidTokenError: Si el token de refresco es inválido
        """
        try:
            # Verificar el token de refresco
            payload = self.verify_token(refresh_token, token_type='refresh')
            
            # Crear nuevo token de acceso
            user_id = payload['sub']
            
            # Copiar claims adicionales del token de refresco (excluyendo los reservados)
            additional_claims = {}
            reserved_claims = {'sub', 'iat', 'exp', 'jti', 'iss', 'aud', 'nbf', 'type'}
            for key, value in payload.items():
                if key not in reserved_claims:
                    additional_claims[key] = value
            
            new_access_token = self.create_access_token(user_id, additional_claims)
            return new_access_token
            
        except InvalidTokenError:
            raise InvalidTokenError("Token de refresco inválido")
    
    def revoke_token(self, token: str) -> bool:
        """
        Marca un token como revocado (implementación básica)
        En producción, usar una lista de revocación o blacklist
        
        Returns:
            True si se procesó la revocación
        """
        # NOTA: En producción, implementar una lista de revocación (RLS)
        # o usar tokens con vida corta y blacklist en Redis
        return True


# Decorador para proteger endpoints (ejemplo para Flask)
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        # Verificar formato "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de autorización inválido. Usar: Bearer <token>'}), 401
        
        token = parts[1]
        
        try:
            # Verificar el token
            jwt_manager = JWTManager()
            payload = jwt_manager.verify_token(token)
            
            # Añadir información del usuario al contexto de la request
            request.user_id = payload['sub']
            request.jwt_payload = payload
            
        except ExpiredSignatureError:
            return jsonify({'error': 'Token ha expirado'}), 401
        except InvalidTokenError as e:
            return jsonify({'error': f'Token inválido: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': 'Error de autenticación'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# Ejemplo de uso
def example_usage():
    """Ejemplo de cómo usar las funciones JWT"""
    
    # Inicializar gestor JWT
    jwt_manager = JWTManager()
    
    # Crear tokens para un usuario
    user_id = "user123"
    
    # Token de acceso con claims adicionales
    access_token = jwt_manager.create_access_token(
        user_id,
        additional_claims={
            'role': 'admin',
            'email': 'usuario@ejemplo.com'
        }
    )
    
    print(f"Token de acceso: {access_token}")
    
    # Token de refresco
    refresh_token = jwt_manager.create_refresh_token(user_id)
    print(f"Token de refresco: {refresh_token}")
    
    # Verificar token
    try:
        payload = jwt_manager.verify_token(access_token)
        print(f"Token válido. Usuario: {payload['sub']}, Rol: {payload.get('role')}")
    except Exception as e:
        print(f"Error verificando token: {e}")
    
    # Refrescar token
    try:
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        print(f"Nuevo token de acceso: {new_access_token}")
    except Exception as e:
        print(f"Error refrescando token: {e}")


# Configuración de seguridad adicional
def security_configuration():
    """
    Configuraciones de seguridad recomendadas para JWT
    """
    recommendations = {
        "1": "Usar HTTPS en producción para prevenir token sniffing",
        "2": "Implementar lista de revocación para tokens comprometidos",
        "3": "Usar vida corta para tokens de acceso (15-60 minutos)",
        "4": "Almacenar tokens de refresco de forma segura (httpOnly cookies)",
        "5": "Implementar rotación de tokens de refresco",
        "6": "Validar siempre issuer y audience",
        "7": "Usar algoritmos fuertes (HS256, RS256)",
        "8": "Proteger la clave secreta (no hardcodear, usar variables de entorno)",
        "9": "Implementar rate limiting para endpoints de autenticación",
        "10": "Registrar y monitorear intentos fallidos de autenticación"
    }
    
    return recommendations


if __name__ == "__main__":
    # Ejecutar ejemplo
    example_usage()
    
    # Mostrar recomendaciones de seguridad
    print("\nRecomendaciones de seguridad:")
    for key, value in security_configuration().items():
        print(f"{key}. {value}")
