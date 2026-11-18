import sqlite3
import hashlib
import secrets
import re
from typing import Optional, Tuple
import bcrypt

class UserManager:
    def __init__(self, db_path: str = "users.db"):
        """Inicializa el gestor de usuarios con la base de datos."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Inicializa la base de datos con la tabla de usuarios si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def _validate_username(self, username: str) -> bool:
        """Valida que el nombre de usuario cumpla con criterios de seguridad."""
        if not username:
            return False
        if len(username) < 3 or len(username) > 30:
            return False
        # Solo permite caracteres alfanuméricos y algunos especiales seguros
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            return False
        return True
    
    def _validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """Valida que la contraseña cumpla con políticas de seguridad."""
        if not password:
            return False, "La contraseña no puede estar vacía"
        
        if len(password) < 12:
            return False, "La contraseña debe tener al menos 12 caracteres"
        
        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales"
        
        # Verificar contraseñas comunes (lista reducida para ejemplo)
        common_passwords = {"password", "123456", "qwerty", "admin", "welcome"}
        if password.lower() in common_passwords:
            return False, "La contraseña es demasiado común"
        
        return True, None
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """Genera un hash seguro de la contraseña usando bcrypt."""
        # bcrypt maneja internamente la generación de salt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt)
        return password_hash.decode('utf-8'), salt.decode('utf-8')
    
    def register_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Registra un nuevo usuario en la base de datos."""
        try:
            # Validar entrada
            if not self._validate_username(username):
                return False, "Nombre de usuario inválido"
            
            is_valid, message = self._validate_password(password)
            if not is_valid:
                return False, message
            
            # Verificar si el usuario ya existe
            if self._user_exists(username):
                return False, "El nombre de usuario ya existe"
            
            # Hash de la contraseña
            password_hash, salt = self._hash_password(password)
            
            # Guardar en la base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, password_hash, salt)
                )
                conn.commit()
            
            return True, "Usuario registrado exitosamente"
            
        except sqlite3.Error as e:
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def _user_exists(self, username: str) -> bool:
        """Verifica si un usuario ya existe en la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
    
    def verify_password(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Verifica las credenciales de un usuario."""
        try:
            # Obtener hash y salt de la base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE username = ?",
                    (username,)
                )
                result = cursor.fetchone()
            
            if not result:
                # Usar tiempo constante para evitar ataques de timing
                self._dummy_verify()
                return False, "Credenciales inválidas"
            
            stored_hash, salt = result
            
            # Verificar contraseña con bcrypt
            password_bytes = password.encode('utf-8')
            salt_bytes = salt.encode('utf-8')
            
            # bcrypt.checkpw maneja la comparación segura contra ataques de timing
            if bcrypt.checkpw(password_bytes, stored_hash.encode('utf-8')):
                return True, "Credenciales válidas"
            else:
                return False, "Credenciales inválidas"
                
        except sqlite3.Error as e:
            return False, f"Error de base de datos: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def _dummy_verify(self) -> None:
        """Realiza una verificación ficticia para mantener tiempo constante."""
        # Esto ayuda a prevenir ataques de timing
        dummy_password = secrets.token_bytes(32)
        dummy_hash = bcrypt.hashpw(dummy_password, bcrypt.gensalt())
        bcrypt.checkpw(dummy_password, dummy_hash)
    
    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        pass  # sqlite3 cierra automáticamente las conexiones

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del gestor de usuarios
    user_manager = UserManager()
    
    # Ejemplo de registro
    username = "usuario_ejemplo"
    password = "ContraseñaSegura123!"
    
    success, message = user_manager.register_user(username, password)
    print(f"Registro: {success} - {message}")
    
    # Ejemplo de verificación exitosa
    success, message = user_manager.verify_password(username, password)
    print(f"Verificación exitosa: {success} - {message}")
    
    # Ejemplo de verificación fallida
    success, message = user_manager.verify_password(username, "contraseña_incorrecta")
    print(f"Verificación fallida: {success} - {message}")
    
    # Limpiar para el ejemplo
    with sqlite3.connect(user_manager.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
