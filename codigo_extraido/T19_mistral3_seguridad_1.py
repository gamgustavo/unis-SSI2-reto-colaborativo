import hashlib
import hmac
import os
import re
import secrets
import logging
from datetime import datetime
from typing import Tuple, Optional

# Configuración segura del logger
logging.basicConfig(
    filename='auth.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constantes de seguridad
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos en segundos
MIN_PASSWORD_LENGTH = 12
SALT_LENGTH = 32
PEPPER = os.getenv('LOGIN_PEPPER', secrets.token_hex(32))  # Debe ser una variable de entorno en producción

# Simulación de base de datos de usuarios (en producción usar una base de datos real)
USER_DB = {
    'admin': {
        'password_hash': '',  # Se establecerá en el primer uso
        'salt': '',
        'login_attempts': 0,
        'last_attempt': 0,
        'locked_until': 0
    }
}

def _validate_password_strength(password: str) -> bool:
    """Valida la fortaleza de la contraseña según políticas de seguridad."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def _hash_password(password: str, salt: str) -> str:
    """Genera un hash seguro de la contraseña usando PBKDF2-HMAC-SHA256."""
    # Combina la contraseña con el pepper (secreto de aplicación)
    peppered_password = password + PEPPER
    # Genera el hash con 100,000 iteraciones
    return hashlib.pbkdf2_hmac(
        'sha256',
        peppered_password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()

def _generate_salt() -> str:
    """Genera un salt criptográficamente seguro."""
    return secrets.token_hex(SALT_LENGTH)

def _is_account_locked(username: str) -> bool:
    """Verifica si la cuenta está bloqueada por intentos fallidos."""
    user_data = USER_DB.get(username)
    if not user_data:
        return False

    current_time = datetime.now().timestamp()
    if user_data['locked_until'] > current_time:
        return True
    return False

def _log_attempt(username: str, success: bool, ip_address: Optional[str] = None) -> None:
    """Registra un intento de inicio de sesión en el archivo de log."""
    status = "SUCCESS" if success else "FAILURE"
    log_message = f"Login attempt - User: {username}, Status: {status}"

    if ip_address:
        log_message += f", IP: {ip_address}"

    if success:
        logging.info(log_message)
    else:
        logging.warning(log_message)

def _reset_login_attempts(username: str) -> None:
    """Reinicia los intentos de inicio de sesión para un usuario."""
    if username in USER_DB:
        USER_DB[username]['login_attempts'] = 0
        USER_DB[username]['last_attempt'] = 0
        USER_DB[username]['locked_until'] = 0

def _increment_login_attempts(username: str) -> None:
    """Incrementa el contador de intentos fallidos y bloquea la cuenta si es necesario."""
    if username not in USER_DB:
        return

    current_time = datetime.now().timestamp()
    USER_DB[username]['login_attempts'] += 1
    USER_DB[username]['last_attempt'] = current_time

    if USER_DB[username]['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
        USER_DB[username]['locked_until'] = current_time + LOCKOUT_TIME

def register_user(username: str, password: str) -> Tuple[bool, str]:
    """Registra un nuevo usuario con contraseña segura."""
    if not username or not password:
        return False, "Usuario y contraseña son requeridos"

    if username in USER_DB:
        return False, "El usuario ya existe"

    if not _validate_password_strength(password):
        return False, (
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres, "
            "incluir mayúsculas, minúsculas, números y símbolos"
        )

    salt = _generate_salt()
    password_hash = _hash_password(password, salt)

    USER_DB[username] = {
        'password_hash': password_hash,
        'salt': salt,
        'login_attempts': 0,
        'last_attempt': 0,
        'locked_until': 0
    }

    _log_attempt(username, True)
    return True, "Usuario registrado exitosamente"

def login(username: str, password: str, ip_address: Optional[str] = None) -> Tuple[bool, str]:
    """
    Intenta iniciar sesión con las credenciales proporcionadas.

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        ip_address: Dirección IP del cliente (opcional, para logging)

    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    # Validaciones iniciales
    if not username or not password:
        _log_attempt(username, False, ip_address)
        return False, "Usuario y contraseña son requeridos"

    if _is_account_locked(username):
        remaining_time = int(USER_DB[username]['locked_until'] - datetime.now().timestamp())
        _log_attempt(username, False, ip_address)
        return False, f"Cuenta bloqueada. Intente nuevamente en {remaining_time} segundos"

    # Verificar si el usuario existe
    if username not in USER_DB:
        # Simular tiempo de procesamiento constante para evitar timing attacks
        secrets.SystemRandom().randint(1, 3)  # Simula tiempo de procesamiento
        _log_attempt(username, False, ip_address)
        return False, "Usuario o contraseña incorrectos"

    # Obtener datos del usuario
    user_data = USER_DB[username]
    salt = user_data['salt']
    stored_hash = user_data['password_hash']

    # Verificar la contraseña de manera segura (constante en tiempo)
    try:
        # Generar el hash de la contraseña proporcionada
        provided_hash = _hash_password(password, salt)

        # Comparación segura de hashes para evitar timing attacks
        if not hmac.compare_digest(stored_hash, provided_hash):
            _increment_login_attempts(username)
            _log_attempt(username, False, ip_address)
            return False, "Usuario o contraseña incorrectos"

        # Inicio de sesión exitoso
        _reset_login_attempts(username)
        _log_attempt(username, True, ip_address)
        return True, "Inicio de sesión exitoso"

    except Exception as e:
        logging.error(f"Error durante el inicio de sesión: {str(e)}")
        _log_attempt(username, False, ip_address)
        return False, "Error durante el inicio de sesión"

# Ejemplo de uso (en producción, esto estaría en otro archivo)
if __name__ == "__main__":
    # Registrar un usuario (solo para demostración)
    register_user("admin", "SecurePassword123!")

    # Intentar iniciar sesión
    success, message = login("admin", "SecurePassword123!", "192.168.1.1")
    print(f"{success}: {message}")
