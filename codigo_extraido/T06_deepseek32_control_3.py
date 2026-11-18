import secrets
import string
import time
from typing import Optional, Tuple
import hashlib
import hmac

class PasswordResetTokenManager:
    def __init__(self, secret_key: str, token_expiry_seconds: int = 3600):
        """
        Inicializa el gestor de tokens de restablecimiento de contraseña.
        
        Args:
            secret_key: Clave secreta para firmar los tokens
            token_expiry_seconds: Tiempo de expiración del token en segundos (por defecto 1 hora)
        """
        self.secret_key = secret_key.encode()
        self.token_expiry_seconds = token_expiry_seconds
    
    def generate_token(self, user_id: str) -> str:
        """
        Genera un token seguro para restablecer la contraseña.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Token de restablecimiento de contraseña
        """
        # Generar un componente aleatorio único
        random_component = secrets.token_urlsafe(32)
        
        # Obtener timestamp actual
        timestamp = str(int(time.time()))
        
        # Crear datos del token
        token_data = f"{user_id}:{timestamp}:{random_component}"
        
        # Calcular HMAC para firmar el token
        signature = hmac.new(
            self.secret_key,
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combinar todo en un token
        token = f"{token_data}:{signature}"
        
        return token
    
    def validate_token(self, token: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un token de restablecimiento de contraseña.
        
        Args:
            token: Token a validar
            user_id: Identificador del usuario que debe coincidir
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        try:
            # Separar las partes del token
            parts = token.split(':')
            if len(parts) != 4:
                return False, "Formato de token inválido"
            
            token_user_id, timestamp_str, random_component, signature = parts
            
            # Verificar que el user_id coincida
            if token_user_id != user_id:
                return False, "Token no corresponde al usuario"
            
            # Verificar la firma
            token_data = f"{token_user_id}:{timestamp_str}:{random_component}"
            expected_signature = hmac.new(
                self.secret_key,
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, "Firma del token inválida"
            
            # Verificar expiración
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            
            if current_time - timestamp > self.token_expiry_seconds:
                return False, "Token expirado"
            
            return True, None
            
        except (ValueError, IndexError) as e:
            return False, f"Error al procesar el token: {str(e)}"

# Funciones de conveniencia para uso directo
def generate_password_reset_token(user_id: str, secret_key: str) -> str:
    """
    Genera un token para restablecer la contraseña.
    
    Args:
        user_id: Identificador único del usuario
        secret_key: Clave secreta para firmar el token
        
    Returns:
        Token de restablecimiento de contraseña
    """
    manager = PasswordResetTokenManager(secret_key)
    return manager.generate_token(user_id)

def validate_password_reset_token(token: str, user_id: str, secret_key: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un token de restablecimiento de contraseña.
    
    Args:
        token: Token a validar
        user_id: Identificador del usuario
        secret_key: Clave secreta usada para firmar el token
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    manager = PasswordResetTokenManager(secret_key)
    return manager.validate_token(token, user_id)

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    SECRET_KEY = "mi_clave_secreta_super_segura"
    USER_ID = "usuario_123"
    
    # Generar token
    token = generate_password_reset_token(USER_ID, SECRET_KEY)
    print(f"Token generado: {token}")
    
    # Validar token (debería ser válido)
    is_valid, error_msg = validate_password_reset_token(token, USER_ID, SECRET_KEY)
    print(f"Token válido: {is_valid}")
    if error_msg:
        print(f"Mensaje de error: {error_msg}")
    
    # Intentar validar con user_id incorrecto
    is_valid, error_msg = validate_password_reset_token(token, "usuario_incorrecto", SECRET_KEY)
    print(f"\nToken con user_id incorrecto válido: {is_valid}")
    if error_msg:
        print(f"Mensaje de error: {error_msg}")
