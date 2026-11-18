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
        """Inicializa la tabla de usuarios si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _validate_username(self, username: str) -> bool:
        """Valida que el nombre de usuario cumpla con requisitos básicos."""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Solo permite caracteres alfanuméricos y algunos símbolos básicos
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False
        
        return True
    
    def _validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """Valida la fortaleza de la contraseña."""
        if len(password) < 12:
            return False, "La contraseña debe tener al menos 12 caracteres"
        
        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "La contraseña debe incluir mayúsculas, minúsculas, números y caracteres especiales"
        
        # Lista de contraseñas comunes (lista reducida para ejemplo)
        common_passwords = {"password123", "1234567890", "qwertyuiop"}
        if password.lower() in common_passwords:
            return False, "La contraseña es demasiado común"
        
        return True, None
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """Genera un hash seguro de la contraseña usando bcrypt."""
        # bcrypt maneja internamente el salt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt)
        return password_hash.decode('utf-8'), salt.decode('utf-8')
    
    def register_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Registra un nuevo usuario de forma segura."""
        
        # Validar entrada
        if not self._validate_username(username):
            return False, "Nombre de usuario inválido"
        
        is_valid, error_msg = self._validate_password(password)
        if not is_valid:
            return False, error_msg
        
        # Verificar si el usuario ya existe
        if self._user_exists(username):
            return False, "El nombre de usuario ya existe"
        
        # Hash de la contraseña
        password_hash, salt = self._hash_password(password)
        
        # Guardar en la base de datos
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, password_hash, salt)
                )
                conn.commit()
            
            # Limpiar variables sensibles de memoria
            del password
            return True, "Usuario registrado exitosamente"
        
        except sqlite3.IntegrityError:
            return False, "Error al registrar el usuario"
        except Exception as e:
            # Log del error (en producción usaría logging)
            print(f"Error inesperado: {e}")
            return False, "Error interno del sistema"
    
    def _user_exists(self, username: str) -> bool:
        """Verifica si un usuario existe."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM users WHERE username = ?",
                    (username,)
                )
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def verify_password(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """Verifica las credenciales del usuario de forma segura."""
        
        # Obtener hash almacenado
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE username = ?",
                    (username,)
                )
                result = cursor.fetchone()
                
                if not result:
                    # Usar tiempo constante para evitar timing attacks
                    bcrypt.hashpw(b"dummy", bcrypt.gensalt())
                    return False, "Credenciales inválidas"
                
                stored_hash = result["password_hash"]
                
                # Verificar contraseña
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8')
                
                # bcrypt.checkpw es resistente a timing attacks
                if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                    return True, "Autenticación exitosa"
                else:
                    return False, "Credenciales inválidas"
        
        except Exception as e:
            # Log del error
            print(f"Error en verificación: {e}")
            return False, "Error interno del sistema"
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """Cambia la contraseña de un usuario de forma segura."""
        
        # Verificar credenciales actuales
        verified, msg = self.verify_password(username, old_password)
        if not verified:
            return False, msg
        
        # Validar nueva contraseña
        is_valid, error_msg = self._validate_password(new_password)
        if not is_valid:
            return False, error_msg
        
        # Generar nuevo hash
        new_hash, new_salt = self._hash_password(new_password)
        
        # Actualizar en la base de datos
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?",
                    (new_hash, new_salt, username)
                )
                
                if cursor.rowcount == 0:
                    return False, "Usuario no encontrado"
                
                conn.commit()
            
            # Limpiar variables sensibles
            del old_password, new_password
            return True, "Contraseña actualizada exitosamente"
        
        except Exception as e:
            print(f"Error al cambiar contraseña: {e}")
            return False, "Error interno del sistema"

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del gestor de usuarios
    user_manager = UserManager()
    
    # Ejemplo de registro
    success, message = user_manager.register_user(
        "usuario_ejemplo",
        "ContraseñaSegura123!"
    )
    print(f"Registro: {success} - {message}")
    
    # Ejemplo de verificación
    if success:
        verified, auth_message = user_manager.verify_password(
            "usuario_ejemplo",
            "ContraseñaSegura123!"
        )
        print(f"Verificación: {verified} - {auth_message}")
        
        # Verificación con contraseña incorrecta
        verified_wrong, wrong_message = user_manager.verify_password(
            "usuario_ejemplo",
            "contraseña_incorrecta"
        )
        print(f"Verificación incorrecta: {verified_wrong} - {wrong_message}")
