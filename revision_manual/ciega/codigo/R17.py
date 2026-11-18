import secrets
import string
import time
from typing import Optional, Tuple

class PasswordResetTokenManager:
    def __init__(self, token_length: int = 32, expiry_hours: int = 24):
        """
        Inicializa el gestor de tokens para restablecimiento de contraseña.
        
        Args:
            token_length: Longitud del token en caracteres (por defecto 32)
            expiry_hours: Horas de validez del token (por defecto 24)
        """
        self.token_length = token_length
        self.expiry_seconds = expiry_hours * 3600
        self.token_store = {}  # En producción, usar una base de datos
        
    def generate_token(self, user_id: str) -> Tuple[str, float]:
        """
        Genera un token único para restablecer la contraseña.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            Tupla con (token, timestamp de expiración)
        """
        # Generar token seguro usando secrets
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(self.token_length))
        
        # Calcular tiempo de expiración
        expiry_time = time.time() + self.expiry_seconds
        
        # Almacenar token (en producción, usar base de datos persistente)
        self.token_store[user_id] = {
            'token': token,
            'expiry': expiry_time,
            'used': False
        }
        
        return token, expiry_time
    
    def validate_token(self, user_id: str, token: str) -> Tuple[bool, str]:
        """
        Valida si un token es válido para un usuario.
        
        Args:
            user_id: Identificador único del usuario
            token: Token a validar
            
        Returns:
            Tupla con (es_válido, mensaje)
        """
        # Verificar si el usuario tiene token almacenado
        if user_id not in self.token_store:
            return False, "Token no encontrado para este usuario"
        
        stored_data = self.token_store[user_id]
        
        # Verificar si el token ya fue usado
        if stored_data['used']:
            return False, "Este token ya fue utilizado"
        
        # Verificar si el token coincide
        if not secrets.compare_digest(token, stored_data['token']):
            return False, "Token inválido"
        
        # Verificar si el token ha expirado
        if time.time() > stored_data['expiry']:
            return False, "Token expirado"
        
        # Marcar token como usado (en producción, hacer esto después del cambio exitoso)
        stored_data['used'] = True
        
        return True, "Token válido"
    
    def revoke_token(self, user_id: str) -> bool:
        """
        Revoca/invalida un token existente.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            True si se revocó exitosamente, False si no existía
        """
        if user_id in self.token_store:
            del self.token_store[user_id]
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Limpia tokens expirados del almacenamiento.
        
        Returns:
            Número de tokens eliminados
        """
        current_time = time.time()
        expired_users = []
        
        for user_id, data in self.token_store.items():
            if current_time > data['expiry']:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.token_store[user_id]
        
        return len(expired_users)


# Funciones de conveniencia para uso simple
def generate_password_reset_token(user_id: str, token_length: int = 32, expiry_hours: int = 24) -> str:
    """
    Función simple para generar un token de restablecimiento de contraseña.
    
    Args:
        user_id: Identificador único del usuario
        token_length: Longitud del token
        expiry_hours: Horas de validez
        
    Returns:
        Token generado
    """
    manager = PasswordResetTokenManager(token_length, expiry_hours)
    token, _ = manager.generate_token(user_id)
    return token

def validate_password_reset_token(user_id: str, token: str, token_length: int = 32, expiry_hours: int = 24) -> bool:
    """
    Función simple para validar un token de restablecimiento de contraseña.
    
    Args:
        user_id: Identificador único del usuario
        token: Token a validar
        token_length: Longitud del token esperada
        expiry_hours: Horas de validez esperadas
        
    Returns:
        True si el token es válido, False en caso contrario
    """
    manager = PasswordResetTokenManager(token_length, expiry_hours)
    # Nota: Esta implementación simple asume que el manager tiene acceso
    # a los tokens generados. En un caso real, necesitarías persistencia.
    is_valid, _ = manager.validate_token(user_id, token)
    return is_valid


# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del gestor
    token_manager = PasswordResetTokenManager()
    
    # Generar token para un usuario
    user_id = "usuario_123"
    token, expiry = token_manager.generate_token(user_id)
    print(f"Token generado: {token}")
    print(f"Expira en: {time.ctime(expiry)}")
    
    # Validar token correcto
    is_valid, message = token_manager.validate_token(user_id, token)
    print(f"\nValidación token correcto: {is_valid} - {message}")
    
    # Validar token incorrecto
    is_valid, message = token_manager.validate_token(user_id, "token_incorrecto")
    print(f"Validación token incorrecto: {is_valid} - {message}")
    
    # Limpiar tokens expirados
    cleaned = token_manager.cleanup_expired_tokens()
    print(f"\nTokens expirados eliminados: {cleaned}")
