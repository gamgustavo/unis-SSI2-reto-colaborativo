import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
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
        """Carga o genera una clave secreta segura"""
        secret_key = os.environ.get('JWT_SECRET_KEY')
        if not secret_key or secret_key == 'default-insecure-key':
            # Generar una clave segura de 64 bytes (512 bits)
            secret_key = secrets.token_urlsafe(64)
            print("ADVERTENCIA: Se generó una nueva clave JWT. Configure JWT_SECRET_KEY en las variables de entorno.")
        return secret_key
    
    def _generate_jti(self) -> str:
        """Genera un identificador único para el token (JWT ID)"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Crea un token JWT de acceso
        
        Args:
            user_id: Identificador único del usuario
            additional_claims: Claims adicionales para incluir en el token
            
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
        
        if additional_claims:
            # Filtrar claims reservados
            reserved_claims = {'sub', 'iat', 'exp', 'jti', 'iss', 'aud', 'nbf', 'type'}
            for key, value in additional_claims.items():
                if key not in reserved_claims:
                    payload[key] = value
        
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Crea un token JWT de refresh
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token JWT de refresh firmado
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
            DecodeError: Si hay un error al decodificar
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
            
            # Verificar el tipo de token
            if payload.get('type') != token_type:
                raise InvalidTokenError(f"Tipo de token incorrecto. Esperado: {token_type}")
            
            # Verificar que el token no sea demasiado viejo (opcional)
            iat = datetime.fromtimestamp(payload['iat'])
            max_age = timedelta(days=30)  # Máximo 30 días de antigüedad
            if datetime.utcnow() - iat > max_age:
                raise InvalidTokenError("Token demasiado viejo")
            
            return payload
            
        except ExpiredSignatureError:
            raise ExpiredSignatureError("Token expirado")
        except DecodeError as e:
            raise DecodeError(f"Error al decodificar el token: {str(e)}")
        except Exception as e:
            raise InvalidTokenError(f"Token inválido: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresca un token de acceso usando un refresh token válido
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Nuevo token de acceso
            
        Raises:
            InvalidTokenError: Si el refresh token es inválido
        """
        try:
            # Verificar el refresh token
            payload = self.verify_token(refresh_token, token_type='refresh')
            
            # Crear nuevo token de acceso
            user_id = payload['sub']
            additional_claims = {k: v for k, v in payload.items() 
                               if k not in ['sub', 'iat', 'exp', 'jti', 'iss', 'aud', 'type']}
            
            return self.create_access_token(user_id, additional_claims)
            
        except Exception as e:
            raise InvalidTokenError(f"No se pudo refrescar el token: {str(e)}")


# Decorador para proteger rutas (ejemplo para Flask)
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        # Verificar formato "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de autorización inválido. Use: Bearer <token>'}), 401
        
        token = parts[1]
        
        try:
            # Obtener instancia de JWTManager (ajustar según tu implementación)
            jwt_manager = current_app.config.get('jwt_manager')
            if not jwt_manager:
                return jsonify({'error': 'Error de configuración JWT'}), 500
                
            payload = jwt_manager.verify_token(token)
            request.user_id = payload['sub']
            request.jwt_payload = payload
            
        except ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except InvalidTokenError as e:
            return jsonify({'error': f'Token inválido: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'Error de autenticación: {str(e)}'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# Función para generar hash seguro de contraseñas (no relacionado directamente con JWT pero importante para seguridad)
def hash_password(password: str) -> str:
    """
    Genera un hash seguro de una contraseña usando PBKDF2
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña en formato hexadecimal
    """
    salt = secrets.token_bytes(32)
    iterations = 100000
    
    # Generar hash usando PBKDF2
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    
    # Combinar salt y hash para almacenamiento
    return f"pbkdf2_sha256${iterations}${salt.hex()}${key.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra un hash almacenado
    
    Args:
        password: Contraseña en texto plano a verificar
        hashed_password: Hash almacenado de la contraseña
        
    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    try:
        # Parsear el formato almacenado
        algorithm, iterations, salt_hex, key_hex = hashed_password.split('$')
        
        if algorithm != 'pbkdf2_sha256':
            return False
            
        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        
        # Calcular hash de la contraseña proporcionada
        computed_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations
        )
        
        # Comparación segura contra timing attacks
        return secrets.compare_digest(computed_key, stored_key)
        
    except (ValueError, AttributeError):
        return False


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar variable de entorno para pruebas
    os.environ['JWT_SECRET_KEY'] = secrets.token_urlsafe(64)
    
    # Crear instancia del manager
    jwt_manager = JWTManager()
    
    # Ejemplo: Crear tokens
    user_id = "user123"
    access_token = jwt_manager.create_access_token(user_id, {"role": "admin"})
    refresh_token = jwt_manager.create_refresh_token(user_id)
    
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    
    # Ejemplo: Verificar token
    try:
        payload = jwt_manager.verify_token(access_token)
        print(f"Token válido. Usuario: {payload['sub']}, Rol: {payload.get('role')}")
    except Exception as e:
        print(f"Error al verificar token: {e}")
    
    # Ejemplo: Refrescar token
    try:
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        print(f"Nuevo Access Token: {new_access_token}")
    except Exception as e:
        print(f"Error al refrescar token: {e}")
    
    # Ejemplo: Hash de contraseña
    password = "mi_contraseña_segura"
    hashed = hash_password(password)
    print(f"Hash de contraseña: {hashed}")
    print(f"Verificación exitosa: {verify_password(password, hashed)}")
    print(f"Verificación fallida: {verify_password('contraseña_incorrecta', hashed)}")
