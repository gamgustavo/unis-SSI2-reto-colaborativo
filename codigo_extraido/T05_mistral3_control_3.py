import sqlite3
from hashlib import sha256
from typing import Optional, Tuple

def inicializar_base_de_datos() -> None:
    """Crea la tabla de usuarios si no existe."""
    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT UNIQUE NOT NULL,
                contrasena_hash TEXT NOT NULL
            )
        ''')
        conn.commit()

def registrar_usuario(nombre_usuario: str, contrasena: str) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario en la base de datos.

    Args:
        nombre_usuario: Nombre del usuario.
        contrasena: Contraseña en texto plano.

    Returns:
        Tuple con (éxito, mensaje).
    """
    if not nombre_usuario or not contrasena:
        return False, "El nombre de usuario y la contraseña no pueden estar vacíos."

    contrasena_hash = sha256(contrasena.encode()).hexdigest()

    try:
        with sqlite3.connect('usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO usuarios (nombre_usuario, contrasena_hash) VALUES (?, ?)',
                (nombre_usuario, contrasena_hash)
            )
            conn.commit()
        return True, "Usuario registrado con éxito."
    except sqlite3.IntegrityError:
        return False, "El nombre de usuario ya existe."

def verificar_contrasena(nombre_usuario: str, contrasena: str) -> Tuple[bool, str]:
    """
    Verifica si la contraseña proporcionada coincide con la almacenada.

    Args:
        nombre_usuario: Nombre del usuario.
        contrasena: Contraseña en texto plano a verificar.

    Returns:
        Tuple con (coincide, mensaje).
    """
    if not nombre_usuario or not contrasena:
        return False, "El nombre de usuario y la contraseña no pueden estar vacíos."

    contrasena_hash = sha256(contrasena.encode()).hexdigest()

    with sqlite3.connect('usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT contrasena_hash FROM usuarios WHERE nombre_usuario = ?',
            (nombre_usuario,)
        )
        resultado = cursor.fetchone()

    if not resultado:
        return False, "Usuario no encontrado."
    elif resultado[0] == contrasena_hash:
        return True, "Contraseña correcta."
    else:
        return False, "Contraseña incorrecta."

# Inicializar la base de datos al importar el módulo
inicializar_base_de_datos()
