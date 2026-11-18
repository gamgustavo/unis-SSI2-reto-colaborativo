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
        
        # Crear el payload
        payload = f"{user_id}:{timestamp}:{random_component}"
        
        # Calcular la firma HMAC
        signature = hmac.new(
            self.secret_key,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combinar payload y firma
        token = f"{payload}:{signature}"
        
        return token
    
    def validate_token(self, token: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un token de restablecimiento de contraseña.
        
        Args:
            token: Token a validar
            user_id: Identificador del usuario que debe coincidir
            
        Returns:
            Tupla (válido, mensaje_de_error)
        """
        try:
            # Separar los componentes del token
            parts = token.split(':')
            if len(parts) != 4:
                return False, "Formato de token inválido"
            
            token_user_id, token_timestamp, random_component, token_signature = parts
            
            # Verificar que el user_id coincida
            if token_user_id != user_id:
                return False, "Token no corresponde al usuario"
            
            # Verificar la firma
            payload = f"{token_user_id}:{token_timestamp}:{random_component}"
            expected_signature = hmac.new(
                self.secret_key,
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(token_signature, expected_signature):
                return False, "Firma del token inválida"
            
            # Verificar la expiración
            try:
                token_time = int(token_timestamp)
                current_time = int(time.time())
                
                if current_time - token_time > self.token_expiry_seconds:
                    return False, "Token expirado"
                
            except ValueError:
                return False, "Timestamp inválido"
            
            return True, "Token válido"
            
        except Exception as e:
            return False, f"Error validando token: {str(e)}"
    
    def generate_simple_token(self, length: int = 32) -> str:
        """
        Genera un token simple (sin firma) para casos más sencillos.
        
        Args:
            length: Longitud del token en caracteres
            
        Returns:
            Token aleatorio seguro
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# Ejemplo de uso:
if __name__ == "__main__":
    # Configurar el gestor de tokens
    SECRET_KEY = "mi-clave-secreta-muy-segura"
    token_manager = PasswordResetTokenManager(SECRET_KEY, token_expiry_seconds=1800)  # 30 minutos
    
    # Generar un token para un usuario
    user_id = "usuario_123"
    token = token_manager.generate_token(user_id)
    print(f"Token generado: {token[:50]}...")
    
    # Validar el token
    is_valid, message = token_manager.validate_token(token, user_id)
    print(f"Token válido: {is_valid}, Mensaje: {message}")
    
    # Generar un token simple
    simple_token = token_manager.generate_simple_token()
    print(f"Token simple: {simple_token}")
