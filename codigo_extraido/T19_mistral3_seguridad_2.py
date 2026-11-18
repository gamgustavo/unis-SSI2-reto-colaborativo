import hashlib
import hmac
import secrets
import logging
from logging.handlers import RotatingFileHandler
from typing import Tuple, Optional
import re
from datetime import datetime

# Configuración segura del logging
def setup_logging() -> logging.Logger:
    logger = logging.getLogger('auth_logger')
    logger.setLevel(logging.INFO)

    # Manejo de rotación de logs para evitar DoS por llenado de disco
    handler = RotatingFileHandler(
        'auth_attempts.log',
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5,
        encoding='utf-8'
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - IP: %(ip)s - User: %(user)s - Status: %(status)s - Message: %(message)s'
    )
    handler.setFormatter(formatter)

    # Filtro personalizado para añadir contexto
    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.ip = getattr(record, 'ip', 'unknown')
            record.user = getattr(record, 'user', 'unknown')
            record.status = getattr(record, 'status', 'unknown')
            return True

    handler.addFilter(ContextFilter())
    logger.addHandler(handler)
    return logger

logger = setup_logging()

# Constantes de seguridad
PEPPER = secrets.token_hex(32)  # Valor secreto único para la aplicación
MIN_PASSWORD_LENGTH = 12
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos en segundos

# Simulación de base de datos de usuarios (en producción usar una base de datos real)
USER_DB = {
    'admin': {
        'password_hash': 'pbkdf2_sha256$260000$...',  # Ejemplo de hash (en producción debe ser real)
        'salt': secrets.token_hex(16),
        'failed_attempts': 0,
        'last_attempt': 0,
        'locked_until': 0
    }
}

def is_account_locked(username: str) -> bool:
    """Verifica si la cuenta está bloqueada por demasiados intentos fallidos."""
    if username not in USER_DB:
        return False

    user_data = USER_DB[username]
    current_time = datetime.now().timestamp()

    if current_time < user_data['locked_until']:
        return True

    # Resetear intentos si el tiempo de bloqueo ha pasado
    if user_data['failed_attempts'] >= MAX_LOGIN_ATTEMPTS:
        user_data['failed_attempts'] = 0
        user_data['locked_until'] = 0
        return False

    return False

def log_attempt(username: str, password: str, ip: str, success: bool) -> None:
    """Registra un intento de autenticación de manera segura."""
    # Sanitizar entradas para evitar inyección en logs
    safe_username = re.sub(r'[^\w\-@.]', '', username) if username else 'unknown'
    safe_ip = re.sub(r'[^\d.]', '', ip) if ip else 'unknown'

    # No registrar la contraseña real, solo su hash parcial para auditoría
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()[:8] if password else 'none'

    # Crear contexto para el log
    extra = {
        'ip': safe_ip,
        'user': safe_username,
        'status': 'success' if success else 'failed'
    }

    if success:
        logger.info(f"Successful login attempt. Password hash prefix: {password_hash}", extra=extra)
    else:
        logger.warning(f"Failed login attempt. Password hash prefix: {password_hash}", extra=extra)

def secure_verify_password(stored_hash: str, provided_password: str, salt: str) -> bool:
    """Verifica una contraseña de manera segura usando PBKDF2."""
    if not provided_password:
        return False

    # Extraer parámetros del hash almacenado (formato: algorithm$iterations$salt$hash)
    try:
        algorithm, iterations, salt, _ = stored_hash.split('$')
        iterations = int(iterations)
    except (ValueError, AttributeError):
        return False

    # Generar hash de la contraseña proporcionada
    new_hash = hashlib.pbkdf2_hmac(
        algorithm.split('_')[-1],  # Obtener el algoritmo (ej: sha256)
        provided_password.encode('utf-8'),
        (salt + PEPPER).encode('utf-8'),
        iterations
    )

    # Comparación segura en tiempo constante
    stored_hash_bytes = stored_hash.split('$')[-1].encode('utf-8')
    return hmac.compare_digest(new_hash, stored_hash_bytes)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Valida la fortaleza de la contraseña según estándares OWASP."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "Password must contain at least one special character"

    common_passwords = ['password', '12345678', 'qwerty', 'admin', 'welcome']
    if password.lower() in common_passwords:
        return False, "Password is too common"

    return True, "Password is strong"

def login(username: str, password: str, ip_address: str) -> Tuple[bool, str]:
    """
    Maneja el proceso de inicio de sesión de manera segura.

    Args:
        username: Nombre de usuario proporcionado
        password: Contraseña proporcionada
        ip_address: Dirección IP del cliente (para logging)

    Returns:
        Tuple con (éxito, mensaje)
    """
    # Validación inicial de entradas
    if not username or not isinstance(username, str):
        log_attempt(username, password, ip_address, False)
        return False, "Invalid username"

    if not password or not isinstance(password, str):
        log_attempt(username, password, ip_address, False)
        return False, "Invalid password"

    # Normalizar username para evitar problemas de mayúsculas/minúsculas
    username = username.strip().lower()

    # Verificar si la cuenta está bloqueada
    if is_account_locked(username):
        log_attempt(username, password, ip_address, False)
        return False, "Account temporarily locked due to too many failed attempts"

    # Verificar si el usuario existe
    if username not in USER_DB:
        # Simular tiempo de procesamiento para evitar timing attacks
        secrets.SystemRandom().randint(1, 100)
        log_attempt(username, password, ip_address, False)
        return False, "Invalid username or password"

    user_data = USER_DB[username]

    # Verificar contraseña
    if not secure_verify_password(user_data['password_hash'], password, user_data['salt']):
        # Incrementar contador de intentos fallidos
        user_data['failed_attempts'] += 1
        user_data['last_attempt'] = datetime.now().timestamp()

        # Bloquear cuenta si se supera el límite
        if user_data['failed_attempts'] >= MAX_LOGIN_ATTEMPTS:
            user_data['locked_until'] = datetime.now().timestamp() + LOCKOUT_TIME
            log_attempt(username, password, ip_address, False)
            return False, "Account locked due to too many failed attempts"

        log_attempt(username, password, ip_address, False)
        return False, "Invalid username or password"

    # Autenticación exitosa
    # Resetear intentos fallidos
    user_data['failed_attempts'] = 0
    user_data['locked_until'] = 0

    log_attempt(username, password, ip_address, True)
    return True, "Login successful"

# Ejemplo de uso seguro
if __name__ == "__main__":
    # Configuración inicial (en producción esto iría en un entorno seguro)
    if 'admin' not in USER_DB:
        # En producción, esto debería hacerse con un proceso seguro de creación de usuarios
        salt = secrets.token_hex(16)
        password = "SecurePassword123!"
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            (salt + PEPPER).encode('utf-8'),
            260000
        ).hex()
        USER_DB['admin'] = {
            'password_hash': f"pbkdf2_sha256$260000${salt}${password_hash}",
            'salt': salt,
            'failed_attempts': 0,
            'last_attempt': 0,
            'locked_until': 0
        }

    # Simulación de login
    test_ip = "192.168.1.1"
    print(login("admin", "SecurePassword123!", test_ip))  # Éxito
    print(login("admin", "wrongpassword", test_ip))      # Fallo
