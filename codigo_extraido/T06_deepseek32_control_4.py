import secrets
import string
import time
from typing import Optional, Tuple

class PasswordResetTokenManager:
    def __init__(self, token_length: int = 32, expiration_hours: int = 24):
        """
        Inicializa el gestor de tokens para restablecimiento de contraseña.
        
        Args:
            token_length: Longitud del token en caracteres (por defecto 32)
            expiration_hours: Horas hasta que el token expire (por defecto 24)
        """
        self.token_length = token_length
        self.expiration_seconds = expiration_hours * 3600
        self.token_store = {}  # En producción, usar una base de datos persistente
        
    def generate_reset_token(self, user_id: str) -> Tuple[str, float]:
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
        expiration_time = time.time() + self.expiration_seconds
        
        # Almacenar token (en producción, guardar en base de datos)
        self.token_store[token] = {
            'user_id': user_id,
            'expiration': expiration_time,
            'used': False
        }
        
        return token, expiration_time
    
    def validate_reset_token(self, token: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Valida si un token de restablecimiento es válido.
        
        Args:
            token: Token a validar
            user_id: Identificador del usuario que solicita la validación
            
        Returns:
            Tupla con (es_válido, mensaje_de_error)
        """
        # Verificar si el token existe
        if token not in self.token_store:
            return False, "Token no válido o no encontrado"
        
        token_data = self.token_store[token]
        
        # Verificar si el token ya fue usado
        if token_data['used']:
            return False, "Este token ya ha sido utilizado"
        
        # Verificar si el token ha expirado
        if time.time() > token_data['expiration']:
            return False, "El token ha expirado"
        
        # Verificar que el token pertenece al usuario correcto
        if token_data['user_id'] != user_id:
            return False, "Token no corresponde al usuario"
        
        # Marcar token como usado (en producción, actualizar en base de datos)
        token_data['used'] = True
        
        return True, None
    
    def cleanup_expired_tokens(self) -> int:
        """
        Elimina tokens expirados del almacenamiento.
        
        Returns:
            Número de tokens eliminados
        """
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.token_store.items()
            if current_time > data['expiration']
        ]
        
        for token in expired_tokens:
            del self.token_store[token]
        
        return len(expired_tokens)


# Funciones de conveniencia para uso simple
def generate_password_reset_token(user_id: str, token_length: int = 32) -> str:
    """
    Función simple para generar un token de restablecimiento.
    
    Args:
        user_id: Identificador del usuario
        token_length: Longitud del token
        
    Returns:
        Token generado
    """
    manager = PasswordResetTokenManager(token_length=token_length)
    token, _ = manager.generate_reset_token(user_id)
    return token


def validate_password_reset_token(token: str, user_id: str) -> bool:
    """
    Función simple para validar un token de restablecimiento.
    
    Args:
        token: Token a validar
        user_id: Identificador del usuario
        
    Returns:
        True si el token es válido, False en caso contrario
    """
    manager = PasswordResetTokenManager()
    is_valid, _ = manager.validate_reset_token(token, user_id)
    return is_valid


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Uso con la clase manager
    manager = PasswordResetTokenManager(expiration_hours=1)
    
    # Generar token para un usuario
    user_id = "usuario_123"
    token, expiration = manager.generate_reset_token(user_id)
    print(f"Token generado: {token}")
    print(f"Expira a las: {time.ctime(expiration)}")
    
    # Validar token (inmediatamente después, debería ser válido)
    is_valid, message = manager.validate_reset_token(token, user_id)
    print(f"Token válido: {is_valid}, Mensaje: {message or 'OK'}")
    
    # Intentar validar nuevamente (debería fallar porque ya fue usado)
    is_valid, message = manager.validate_reset_token(token, user_id)
    print(f"Token válido (segundo intento): {is_valid}, Mensaje: {message}")
    
    # Ejemplo 2: Uso con las funciones simples
    simple_token = generate_password_reset_token("usuario_456", token_length=16)
    print(f"\nToken simple generado: {simple_token}")
    
    is_valid_simple = validate_password_reset_token(simple_token, "usuario_456")
    print(f"Token simple válido: {is_valid_simple}")
