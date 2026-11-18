import hashlib
import hmac
import os
import re
import secrets
import time
from datetime import datetime
from typing import Optional, Tuple

# Configuración segura
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos en segundos
LOG_FILE = "login_attempts.log"
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))  # Debe ser configurado en producción
PASSWORD_MIN_LENGTH = 12
SALT_LENGTH = 32

# Expresión regular para validar usuarios (solo letras, números y guiones bajos)
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')

def _validate_username(username: str) -> bool:
    """Valida que el nombre de usuario cumpla con los requisitos de seguridad."""
    if not USERNAME_REGEX.match(username):
        return False
    if len(username) < 4 or len(username) > 32:
        return False
    return True

def _validate_password(password: str) -> bool:
    """Valida que la contraseña cumpla con los requisitos de seguridad."""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False
    # Verificar complejidad (al menos una mayúscula, una minúscula, un número y un carácter especial)
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True

def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Genera un hash seguro de la contraseña usando PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_hex(SALT_LENGTH)
    else:
        salt = salt.encode('utf-8')
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Número de iteraciones
    )
    return salt.hex(), password_hash.hex()

def _verify_password(stored_hash: str, stored_salt: str, provided_password: str) -> bool:
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    salt, original_hash = stored_salt, stored_hash
    _, new_hash = _hash_password(provided_password, salt)
    return hmac.compare_digest(original_hash, new_hash)

def _log_attempt(username: str, success: bool, ip_address: str = "unknown") -> None:
    """Registra un intento de inicio de sesión en el archivo de log."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - IP: {ip_address} - User: {username} - {'SUCCESS' if success else 'FAILURE'}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except IOError as e:
        # En producción, deberías manejar esto de manera más robusta (ej: syslog, servicio externo)
        print(f"Error writing to log file: {e}")

def _is_account_locked(username: str) -> bool:
    """Verifica si la cuenta está bloqueada por demasiados intentos fallidos."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as log_file:
            attempts = 0
            now = time.time()
            for line in log_file:
                if f"User: {username} - FAILURE" in line:
                    # Extraer timestamp de la línea de log
                    timestamp_str = line.split(" - ")[0]
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str).timestamp()
                        if now - timestamp < LOCKOUT_TIME:
                            attempts += 1
                            if attempts >= MAX_LOGIN_ATTEMPTS:
                                return True
                    except ValueError:
                        continue
    except IOError:
        pass
    return False

def login(username: str, password: str, ip_address: str = "unknown") -> bool:
    """
    Intenta iniciar sesión con las credenciales proporcionadas.

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        ip_address: Dirección IP del cliente (para logging)

    Returns:
        bool: True si el inicio de sesión fue exitoso, False en caso contrario
    """
    # Validación inicial
    if not _validate_username(username):
        _log_attempt(username, False, ip_address)
        return False

    if not _validate_password(password):
        _log_attempt(username, False, ip_address)
        return False

    # Verificar si la cuenta está bloqueada
    if _is_account_locked(username):
        _log_attempt(username, False, ip_address)
        return False

    # Aquí iría la lógica real para verificar las credenciales contra una base de datos
    # Este es un ejemplo simplificado con credenciales hardcodeadas (NO USAR EN PRODUCCIÓN)
    # En producción, usa una base de datos segura con hashes de contraseñas

    # Ejemplo de credenciales almacenadas (solo para demostración)
    # En producción, esto debería venir de una base de datos segura
    stored_users = {
        "admin": {
            "salt": "a1b2c3d4e5f6...",  # Debe ser único por usuario
            "hash": "hashed_password_here"  # Hash generado con _hash_password
        }
    }

    if username not in stored_users:
        _log_attempt(username, False, ip_address)
        return False

    stored_user = stored_users[username]
    if _verify_password(stored_user["hash"], stored_user["salt"], password):
        _log_attempt(username, True, ip_address)
        return True
    else:
        _log_attempt(username, False, ip_address)
        return False

# Ejemplo de uso (solo para testing)
if __name__ == "__main__":
    # Esto es solo para demostración. En producción, no uses credenciales hardcodeadas.
    test_username = "admin"
    test_password = "SecurePassword123!"

    # Configurar credenciales de prueba (solo para este ejemplo)
    salt, pwd_hash = _hash_password(test_password)
    stored_users = {
        test_username: {
            "salt": salt,
            "hash": pwd_hash
        }
    }

    # Simular un inicio de sesión
    print("Login successful:" if login(test_username, test_password) else "Login failed")
