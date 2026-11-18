import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

# Configuración segura
LOG_FILE = "auth_attempts.log"
DB_FILE = "users.db"
SECRET_KEY = secrets.token_hex(32)  # Clave secreta para HMAC
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutos en segundos
MIN_PASSWORD_LENGTH = 12
SALT_LENGTH = 16

# Expresión regular para validar contraseñas
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\-{}\[\]:\";'<>?,./]).+$"
)

def initialize_database() -> None:
    """Inicializa la base de datos con la tabla de usuarios si no existe."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                login_attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                locked_until TIMESTAMP
            )
        """)
        conn.commit()

def log_attempt(username: str, success: bool, ip_address: Optional[str] = None) -> None:
    """Registra un intento de inicio de sesión en el archivo de log."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - Usuario: {username} - IP: {ip_address or 'N/A'} - {'ÉXITO' if success else 'FALLIDO'}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def hash_password(password: str, salt: str) -> str:
    """Genera un hash seguro de la contraseña usando PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000  # Número de iteraciones
    ).hex()

def verify_password(stored_hash: str, provided_password: str, salt: str) -> bool:
    """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
    new_hash = hash_password(provided_password, salt)
    return hmac.compare_digest(stored_hash, new_hash)

def validate_password(password: str) -> bool:
    """Valida que la contraseña cumpla con los requisitos de seguridad."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if not PASSWORD_REGEX.match(password):
        return False
    return True

def is_account_locked(username: str) -> bool:
    """Verifica si la cuenta está bloqueada por demasiados intentos fallidos."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT locked_until FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()

        if result and result[0]:
            locked_until = datetime.fromisoformat(result[0])
            if datetime.now() < locked_until:
                return True
            # Desbloquear la cuenta si el tiempo de bloqueo ha pasado
            cursor.execute(
                "UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?",
                (username,)
            )
            conn.commit()
    return False

def increment_failed_attempts(username: str) -> None:
    """Incrementa el contador de intentos fallidos y bloquea la cuenta si es necesario."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT login_attempts FROM users WHERE username = ?",
            (username,)
        )
        attempts = cursor.fetchone()[0] + 1 if cursor.fetchone() else 1

        if attempts >= MAX_LOGIN_ATTEMPTS:
            locked_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
            cursor.execute(
                "UPDATE users SET login_attempts = ?, locked_until = ? WHERE username = ?",
                (attempts, locked_until.isoformat(), username)
            )
        else:
            cursor.execute(
                "UPDATE users SET login_attempts = ? WHERE username = ?",
                (attempts, username)
            )
        conn.commit()

def login(username: str, password: str, ip_address: Optional[str] = None) -> Tuple[bool, str]:
    """
    Intenta iniciar sesión con las credenciales proporcionadas.

    Args:
        username: Nombre de usuario.
        password: Contraseña en texto plano.
        ip_address: Dirección IP del cliente (opcional).

    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    if not username or not password:
        log_attempt(username, False, ip_address)
        return False, "Usuario y contraseña son obligatorios."

    if is_account_locked(username):
        log_attempt(username, False, ip_address)
        return False, "Cuenta bloqueada por demasiados intentos fallidos. Intente más tarde."

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash, salt FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()

        if not result:
            # Simular tiempo de espera para evitar enumeración de usuarios
            secrets.SystemRandom().randint(1, 3)
            log_attempt(username, False, ip_address)
            return False, "Usuario o contraseña incorrectos."

        stored_hash, salt = result

        if verify_password(stored_hash, password, salt):
            # Reiniciar intentos fallidos en inicio de sesión exitoso
            cursor.execute(
                "UPDATE users SET login_attempts = 0, last_attempt = ?, locked_until = NULL WHERE username = ?",
                (datetime.now().isoformat(), username)
            )
            conn.commit()
            log_attempt(username, True, ip_address)
            return True, "Inicio de sesión exitoso."
        else:
            increment_failed_attempts(username)
            log_attempt(username, False, ip_address)
            return False, "Usuario o contraseña incorrectos."

def register_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario con contraseña segura.

    Args:
        username: Nombre de usuario.
        password: Contraseña en texto plano.

    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    if not username or not password:
        return False, "Usuario y contraseña son obligatorios."

    if not validate_password(password):
        return False, (
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres, "
            "incluir mayúsculas, minúsculas, números y símbolos."
        )

    salt = secrets.token_hex(SALT_LENGTH)
    password_hash = hash_password(password, salt)

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt)
            )
            conn.commit()
        return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError:
        return False, "El nombre de usuario ya existe."

# Inicializar la base de datos al importar el módulo
initialize_database()
