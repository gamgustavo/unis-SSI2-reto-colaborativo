import sqlite3
from hashlib import sha256
import os
import secrets

# Configuración de la base de datos
DATABASE_NAME = 'users.db'

def init_db():
    """Inicializa la base de datos con la tabla de usuarios."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str, salt: str) -> str:
    """Genera un hash seguro de la contraseña usando SHA-256 y una sal."""
    return sha256((password + salt).encode()).hexdigest()

def register_user(username: str, password: str) -> bool:
    """
    Registra un nuevo usuario en la base de datos.
    Retorna True si el registro fue exitoso, False si el usuario ya existe.
    """
    if not username or not password:
        return False

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
            (username, password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_password(username: str, password: str) -> bool:
    """
    Verifica si la contraseña proporcionada coincide con la almacenada.
    Retorna True si la contraseña es correcta, False en caso contrario.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT password_hash, salt FROM users WHERE username = ?',
        (username,)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        return False

    stored_hash, salt = result
    input_hash = hash_password(password, salt)
    return secrets.compare_digest(stored_hash, input_hash)

# Inicializar la base de datos al importar el módulo
init_db()
