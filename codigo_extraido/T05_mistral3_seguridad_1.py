import os
import sqlite3
import hashlib
import secrets
import re
from typing import Tuple, Optional
from dataclasses import dataclass

# Configuración de seguridad
PEPPER = os.getenv('PASSWORD_PEPPER', secrets.token_hex(32))  # Debe ser una variable de entorno en producción
SALT_LENGTH = 32
HASH_ALGORITHM = 'sha256'
ITERATIONS = 100000
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 64

# Inicialización de la base de datos
def init_db(db_path: str = 'users.db') -> None:
    """Inicializa la base de datos con la tabla de usuarios."""
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            iterations INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_attempts INTEGER DEFAULT 0,
            account_locked BOOLEAN DEFAULT FALSE
        )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        conn.commit()

@dataclass
class User:
    username: str
    password_hash: str
    salt: str
    iterations: int

def validate_password(password: str) -> Tuple[bool, str]:
    """Valida la fortaleza de la contraseña según políticas de seguridad."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"La contraseña no puede exceder {MAX_PASSWORD_LENGTH} caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "La contraseña debe contener al menos un carácter especial"
    if re.search(r'(.)\1{2,}', password):  # Evita secuencias repetidas
        return False, "La contraseña contiene caracteres repetidos en secuencia"
    common_passwords = ['password', '12345678', 'qwertyuiop', 'contraseña']
    if password.lower() in common_passwords:
        return False, "La contraseña es demasiado común"
    return True, "Contraseña válida"

def hash_password(password: str, salt: Optional[str] = None, iterations: Optional[int] = None) -> Tuple[str, str, int]:
    """Genera un hash seguro de la contraseña usando PBKDF2."""
    if salt is None:
        salt = secrets.token_hex(SALT_LENGTH)
    if iterations is None:
        iterations = ITERATIONS

    # Combina la contraseña con el pepper (secreto global)
    peppered_password = password + PEPPER

    # Genera el hash usando PBKDF2
    password_hash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        peppered_password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations
    ).hex()

    return password_hash, salt, iterations

def register_user(username: str, password: str, db_path: str = 'users.db') -> Tuple[bool, str]:
    """Registra un nuevo usuario con contraseña segura."""
    # Validar entrada
    if not username or not password:
        return False, "El nombre de usuario y contraseña son obligatorios"

    if len(username) < 4 or len(username) > 32:
        return False, "El nombre de usuario debe tener entre 4 y 32 caracteres"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "El nombre de usuario solo puede contener letras, números y guiones bajos"

    # Validar fortaleza de la contraseña
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message

    # Verificar si el usuario ya existe
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False, "El nombre de usuario ya existe"
    except sqlite3.Error as e:
        return False, f"Error al acceder a la base de datos: {str(e)}"

    # Generar hash de la contraseña
    try:
        password_hash, salt, iterations = hash_password(password)
    except Exception as e:
        return False, f"Error al generar el hash de la contraseña: {str(e)}"

    # Guardar usuario en la base de datos
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                'INSERT INTO users (username, password_hash, salt, iterations) VALUES (?, ?, ?, ?)',
                (username, password_hash, salt, iterations)
            )
            conn.commit()
        return True, "Usuario registrado exitosamente"
    except sqlite3.IntegrityError:
        return False, "El nombre de usuario ya existe (error de concurrencia)"
    except sqlite3.Error as e:
        return False, f"Error al guardar el usuario: {str(e)}"

def verify_password(username: str, password: str, db_path: str = 'users.db') -> Tuple[bool, str]:
    """Verifica la contraseña de un usuario con protección contra ataques."""
    # Validar entrada
    if not username or not password:
        return False, "El nombre de usuario y contraseña son obligatorios"

    # Obtener información del usuario
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password_hash, salt, iterations, failed_attempts, account_locked
                FROM users
                WHERE username = ?
            ''', (username,))
            user_data = cursor.fetchone()

            if not user_data:
                # Simular tiempo de espera para evitar enumeración de usuarios
                secrets.SystemRandom().randint(1, 3)  # Simula tiempo de procesamiento
                return False, "Usuario o contraseña incorrectos"

            if user_data['account_locked']:
                return False, "La cuenta está bloqueada por demasiados intentos fallidos"

            # Verificar contraseña
            stored_hash = user_data['password_hash']
            salt = user_data['salt']
            iterations = user_data['iterations']

            # Generar hash de la contraseña proporcionada
            input_hash, _, _ = hash_password(password, salt, iterations)

            if secrets.compare_digest(stored_hash, input_hash):
                # Contraseña correcta - resetear intentos fallidos
                cursor.execute('''
                    UPDATE users
                    SET failed_attempts = 0, last_login = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (username,))
                conn.commit()
                return True, "Autenticación exitosa"
            else:
                # Contraseña incorrecta - incrementar intentos fallidos
                failed_attempts = user_data['failed_attempts'] + 1
                if failed_attempts >= 5:
                    cursor.execute('''
                        UPDATE users
                        SET failed_attempts = ?, account_locked = TRUE
                        WHERE username = ?
                    ''', (failed_attempts, username))
                    conn.commit()
                    return False, "Cuenta bloqueada por demasiados intentos fallidos"
                else:
                    cursor.execute('''
                        UPDATE users
                        SET failed_attempts = ?
                        WHERE username = ?
                    ''', (failed_attempts, username))
                    conn.commit()
                    return False, "Usuario o contraseña incorrectos"

    except sqlite3.Error as e:
        return False, f"Error al verificar la contraseña: {str(e)}"

def unlock_account(username: str, db_path: str = 'users.db') -> Tuple[bool, str]:
    """Desbloquea una cuenta bloqueada por demasiados intentos fallidos."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET failed_attempts = 0, account_locked = FALSE
                WHERE username = ?
            ''', (username,))
            if cursor.rowcount == 0:
                return False, "Usuario no encontrado o no estaba bloqueado"
            conn.commit()
            return True, "Cuenta desbloqueada exitosamente"
    except sqlite3.Error as e:
        return False, f"Error al desbloquear la cuenta: {str(e)}"

# Inicializar la base de datos al importar el módulo
init_db()
