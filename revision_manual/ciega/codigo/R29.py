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
            try:
                timestamp = int(timestamp_str)
                current_time = int(time.time())
                
                if current_time - timestamp > self.token_expiry_seconds:
                    return False, "Token expirado"
                
            except ValueError:
                return False, "Timestamp inválido"
            
            return True, "Token válido"
            
        except Exception as e:
            return False, f"Error validando token: {str(e)}"
    
    def generate_simple_token(self, length: int = 32) -> str:
        """
        Genera un token simple (sin firma) para casos más simples.
        
        Args:
            length: Longitud del token en caracteres
            
        Returns:
            Token aleatorio seguro
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# Funciones de conveniencia para uso directo
def generate_password_reset_token(secret_key: str, user_id: str, expiry_seconds: int = 3600) -> str:
    """
    Función para generar un token de restablecimiento de contraseña.
    
    Args:
        secret_key: Clave secreta para firmar
        user_id: ID del usuario
        expiry_seconds: Tiempo de expiración en segundos
        
    Returns:
        Token generado
    """
    manager = PasswordResetTokenManager(secret_key, expiry_seconds)
    return manager.generate_token(user_id)


def validate_password_reset_token(secret_key: str, token: str, user_id: str) -> Tuple[bool, Optional[str]]:
    """
    Función para validar un token de restablecimiento de contraseña.
    
    Args:
        secret_key: Clave secreta para verificar
        token: Token a validar
        user_id: ID del usuario esperado
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    manager = PasswordResetTokenManager(secret_key)
    return manager.validate_token(token, user_id)


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    SECRET_KEY = "mi-clave-secreta-muy-segura"
    USER_ID = "usuario_123"
    
    # Generar token
    token = generate_password_reset_token(SECRET_KEY, USER_ID)
    print(f"Token generado: {token[:50]}...")
    
    # Validar token (caso exitoso)
    is_valid, message = validate_password_reset_token(SECRET_KEY, token, USER_ID)
    print(f"Validación exitosa: {is_valid}, Mensaje: {message}")
    
    # Validar token (caso fallido - usuario incorrecto)
    is_valid, message = validate_password_reset_token(SECRET_KEY, token, "usuario_incorrecto")
    print(f"Validación fallida (usuario incorrecto): {is_valid}, Mensaje: {message}")
    
    # Generar token simple
    simple_token = PasswordResetTokenManager(SECRET_KEY).generate_simple_token()
    print(f"Token simple: {simple_token}")
