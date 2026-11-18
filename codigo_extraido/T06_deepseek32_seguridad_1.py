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
    def __init__(self, secret_key: str, token_expiry_hours: int = 24, token_length: int = 32):
        """
        Inicializa el gestor de tokens de restablecimiento de contraseña.
        
        Args:
            secret_key: Clave secreta para firmar los tokens (debe ser larga y aleatoria)
            token_expiry_hours: Horas de validez del token (por defecto 24)
            token_length: Longitud del token aleatorio en bytes (por defecto 32)
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("La clave secreta debe tener al menos 32 caracteres")
        
        self.secret_key = secret_key.encode('utf-8')
        self.token_expiry_hours = token_expiry_hours
        self.token_length = token_length
    
    def _generate_random_token(self) -> str:
        """Genera un token criptográficamente seguro."""
        return secrets.token_urlsafe(self.token_length)
    
    def _create_signature(self, data: str) -> str:
        """Crea un HMAC-SHA256 signature para los datos."""
        return hmac.new(
            self.secret_key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verifica la firma HMAC de los datos."""
        expected_signature = self._create_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def generate_reset_token(self, user_id: str) -> str:
        """
        Genera un token seguro para restablecer la contraseña.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token codificado en base64 seguro para URL
        """
        # Validación de entrada
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id debe ser una cadena no vacía")
        
        # Generar token único
        random_token = self._generate_random_token()
        
        # Crear payload con timestamp de expiración
        expiry_time = int(time.time()) + (self.token_expiry_hours * 3600)
        payload = {
            'user_id': user_id,
            'token': random_token,
            'exp': expiry_time,
            'iat': int(time.time())
        }
        
        # Convertir payload a JSON y luego a base64
        payload_json = json.dumps(payload, separators=(',', ':'))  # Compact JSON
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8')
        
        # Crear firma
        signature = self._create_signature(payload_b64)
        
        # Combinar payload y firma
        token = f"{payload_b64}.{signature}"
        
        return token
    
    def validate_reset_token(self, token: str) -> TokenValidationResult:
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
        
        payload_b64, signature = parts
        
        # Verificar firma
        if not self._verify_signature(payload_b64, signature):
            return TokenValidationResult(
                is_valid=False,
                error_message="Firma inválida"
            )
        
        try:
            # Decodificar payload
            payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Validar campos requeridos
            required_fields = ['user_id', 'token', 'exp', 'iat']
            for field in required_fields:
                if field not in payload:
                    return TokenValidationResult(
                        is_valid=False,
                        error_message=f"Campo '{field}' faltante en el token"
                    )
            
            # Verificar expiración
            current_time = int(time.time())
            if current_time > payload['exp']:
                return TokenValidationResult(
                    is_valid=False,
                    user_id=payload['user_id'],
                    error_message="Token expirado"
                )
            
            # Verificar timestamp de emisión (no puede estar en el futuro)
            if payload['iat'] > current_time + 60:  # 60 segundos de tolerancia
                return TokenValidationResult(
                    is_valid=False,
                    user_id=payload['user_id'],
                    error_message="Timestamp de emisión inválido"
                )
            
            # Validar longitud del token aleatorio
            if len(payload['token']) < self.token_length * 0.75:  # Aproximado para base64
                return TokenValidationResult(
                    is_valid=False,
                    user_id=payload['user_id'],
                    error_message="Token aleatorio inválido"
                )
            
            return TokenValidationResult(
                is_valid=True,
                user_id=payload['user_id']
            )
            
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError) as e:
            return TokenValidationResult(
                is_valid=False,
                error_message=f"Error decodificando el token: {str(e)}"
            )
        except Exception as e:
            return TokenValidationResult(
                is_valid=False,
                error_message=f"Error validando el token: {str(e)}"
            )
    
    def invalidate_token(self, token: str) -> bool:
        """
        Marca un token como utilizado/inválido.
        En una implementación real, esto almacenaría el token en una lista negra.
        
        Args:
            token: Token a invalidar
            
        Returns:
            True si se invalidó correctamente
        """
        # En una implementación real, aquí se almacenaría el token
        # en una base de datos o caché como utilizado
        # Por simplicidad, solo validamos el formato
        validation = self.validate_reset_token(token)
        return validation.is_valid


# Ejemplo de uso
if __name__ == "__main__":
    # IMPORTANTE: En producción, usa una clave secreta segura y guárdala de forma segura
    # Ejemplo: secrets.token_urlsafe(64)
    SECRET_KEY = "tu_clave_secreta_muy_larga_y_aleatoria_aqui_minimo_32_caracteres"
    
    # Crear instancia del gestor de tokens
    token_manager = PasswordResetTokenManager(
        secret_key=SECRET_KEY,
        token_expiry_hours=24,
        token_length=32
    )
    
    # Ejemplo: Generar token para un usuario
    user_id = "usuario_123"
    try:
        reset_token = token_manager.generate_reset_token(user_id)
        print(f"Token generado: {reset_token[:50]}...")
        
        # Ejemplo: Validar token
        validation_result = token_manager.validate_reset_token(reset_token)
        
        if validation_result.is_valid:
            print(f"Token válido para el usuario: {validation_result.user_id}")
            # Proceder con el restablecimiento de contraseña
        else:
            print(f"Token inválido: {validation_result.error_message}")
            
        # Ejemplo: Token expirado (simulado)
        expired_token = "eyJ1c2VyX2lkIjoidXN1YXJpb18xMjMiLCJ0b2tlbiI6ImlBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU
