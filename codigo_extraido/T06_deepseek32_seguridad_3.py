import secrets
import string
import hashlib
import hmac
import time
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import base64

@dataclass
class TokenValidationResult:
    is_valid: bool
    user_id: Optional[str] = None
    error_message: Optional[str] = None

class PasswordResetTokenManager:
    def __init__(self, secret_key: str, token_expiry_hours: int = 24, algorithm: str = 'sha256'):
        """
        Inicializa el gestor de tokens de restablecimiento de contraseña.
        
        Args:
            secret_key: Clave secreta para firmar los tokens (debe ser larga y aleatoria)
            token_expiry_hours: Horas de validez del token (por defecto 24)
            algorithm: Algoritmo de hash para la firma (por defecto sha256)
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("La clave secreta debe tener al menos 32 caracteres")
        
        self.secret_key = secret_key.encode('utf-8')
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = algorithm
        self.token_length = 32  # Longitud del token aleatorio
    
    def _generate_random_token(self) -> str:
        """Genera un token criptográficamente seguro."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(self.token_length))
    
    def _create_signature(self, data: str) -> str:
        """Crea una firma HMAC para los datos."""
        return hmac.new(
            self.secret_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verifica la firma HMAC de los datos."""
        expected_signature = self._create_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def generate_token(self, user_id: str) -> str:
        """
        Genera un token seguro para restablecer la contraseña.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token codificado en base64 URL-safe
        """
        # Validación de entrada
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id debe ser una cadena no vacía")
        
        # Generar componentes del token
        token_id = self._generate_random_token()
        creation_time = int(time.time())
        expiry_time = creation_time + (self.token_expiry_hours * 3600)
        
        # Crear payload
        payload = {
            'user_id': user_id,
            'token_id': token_id,
            'created_at': creation_time,
            'expires_at': expiry_time,
            'version': '1.0'
        }
        
        # Convertir a JSON y codificar
        payload_json = json.dumps(payload, separators=(',', ':'))  # Compacto
        payload_encoded = base64.urlsafe_b64encode(
            payload_json.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        # Crear firma
        signature = self._create_signature(payload_encoded)
        
        # Combinar payload y firma
        token = f"{payload_encoded}.{signature}"
        
        return token
    
    def validate_token(self, token: str) -> TokenValidationResult:
        """
        Valida un token de restablecimiento de contraseña.
        
        Args:
            token: Token a validar
            
        Returns:
            TokenValidationResult con el resultado de la validación
        """
        # Validación básica del token
        if not token or not isinstance(token, str):
            return TokenValidationResult(
                is_valid=False,
                error_message="Token inválido o vacío"
            )
        
        # Separar payload y firma
        parts = token.split('.')
        if len(parts) != 2:
            return TokenValidationResult(
                is_valid=False,
                error_message="Formato de token inválido"
            )
        
        payload_encoded, signature = parts
        
        # Verificar firma
        if not self._verify_signature(payload_encoded, signature):
            return TokenValidationResult(
                is_valid=False,
                error_message="Firma inválida"
            )
        
        try:
            # Decodificar payload
            # Añadir padding si es necesario
            padding_needed = 4 - len(payload_encoded) % 4
            if padding_needed != 4:
                payload_encoded += '=' * padding_needed
            
            payload_json = base64.urlsafe_b64decode(payload_encoded).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Validar estructura del payload
            required_fields = ['user_id', 'token_id', 'created_at', 'expires_at', 'version']
            for field in required_fields:
                if field not in payload:
                    return TokenValidationResult(
                        is_valid=False,
                        error_message=f"Campo '{field}' faltante en el token"
                    )
            
            # Verificar versión
            if payload['version'] != '1.0':
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Versión de token no soportada"
                )
            
            # Verificar expiración
            current_time = int(time.time())
            if current_time > payload['expires_at']:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Token expirado"
                )
            
            # Verificar que created_at sea anterior a expires_at
            if payload['created_at'] >= payload['expires_at']:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Timestamp de creación inválido"
                )
            
            # Verificar que el token no sea del futuro (con margen de 5 minutos)
            if payload['created_at'] > current_time + 300:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Timestamp de creación en el futuro"
                )
            
            # Validar formato del user_id
            user_id = payload['user_id']
            if not user_id or not isinstance(user_id, str) or len(user_id) > 255:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="user_id inválido"
                )
            
            # Validar formato del token_id
            token_id = payload['token_id']
            if not token_id or not isinstance(token_id, str) or len(token_id) != self.token_length:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="token_id inválido"
                )
            
            return TokenValidationResult(
                is_valid=True,
                user_id=user_id
            )
            
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
            return TokenValidationResult(
                is_valid=False,
                error_message=f"Error decodificando token: {str(e)}"
            )
        except Exception as e:
            # Captura genérica para evitar fugas de información
            return TokenValidationResult(
                is_valid=False,
                error_message="Error procesando token"
            )
    
    def invalidate_token(self, token: str) -> bool:
        """
        Marca un token como utilizado/inválido.
        En una implementación real, esto registraría el token en una lista negra.
        
        Args:
            token: Token a invalidar
            
        Returns:
            True si se invalidó correctamente
        """
        # En una implementación completa, aquí se guardaría el token
        # en una base de datos o caché como utilizado
        validation_result = self.validate_token(token)
        if validation_result.is_valid:
            # Registrar token como utilizado (implementación específica)
            # Ejemplo: self._blacklist_token(token, validation_result.user_id)
            pass
        return validation_result.is_valid


# Ejemplo de uso
if __name__ == "__main__":
    # Clave secreta (en producción, obtener de variables de entorno)
    SECRET_KEY = secrets.token_urlsafe(64)
    
    # Crear instancia del gestor de tokens
    token_manager = PasswordResetTokenManager(
        secret_key=SECRET_KEY,
        token_expiry_hours=24
    )
    
    # Ejemplo: Generar token para un usuario
    user_id = "usuario_123"
    try:
        token = token_manager.generate_token(user_id)
        print(f"Token generado: {token[:50]}...")
        
        # Validar token
        validation_result = token_manager.validate_token(token)
        
        if validation_result.is_valid:
            print(f"Token válido para usuario: {validation_result.user_id}")
            
            # Invalidar token después de uso
            token_manager.invalidate_token(token)
            print("Token marcado como utilizado")
        else:
            print(f"Token inválido: {validation_result.error_message}")
            
    except ValueError as e:
        print(f"Error: {e}")
    
    # Ejemplo de token inválido
    invalid_token = "token.invalido"
    invalid_result = token_manager.validate_token(invalid_token)
    print(f"\nValidación token inválido: {invalid_result.error_message}")
