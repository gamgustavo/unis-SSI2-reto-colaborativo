import sqlite3
from hashlib import sha256
from getpass import getpass

def inicializar_base_de_datos():
    """Crea la tabla de usuarios si no existe."""
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            contrasena_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def registrar_usuario(nombre_usuario, contrasena):
    """
    Registra un nuevo usuario en la base de datos.

    Args:
        nombre_usuario (str): Nombre del usuario.
        contrasena (str): Contraseña del usuario (se almacenará como hash).

    Returns:
        bool: True si el registro fue exitoso, False si el usuario ya existe.
    """
    contrasena_hash = sha256(contrasena.encode()).hexdigest()

    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre_usuario, contrasena_hash)
            VALUES (?, ?)
        ''', (nombre_usuario, contrasena_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_contrasena(nombre_usuario, contrasena):
    """
    Verifica si la contraseña proporcionada coincide con la almacenada.

    Args:
        nombre_usuario (str): Nombre del usuario.
        contrasena (str): Contraseña a verificar.

    Returns:
        bool: True si la contraseña es correcta, False en caso contrario.
    """
    contrasena_hash = sha256(contrasena.encode()).hexdigest()

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT contrasena_hash FROM usuarios
        WHERE nombre_usuario = ?
    ''', (nombre_usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado and resultado[0] == contrasena_hash:
        return True
    return False

# Ejemplo de uso (descomentar para probar)
if __name__ == "__main__":
    inicializar_base_de_datos()

    # Registro
    usuario = input("Ingrese nombre de usuario para registrar: ")
    contrasena = getpass("Ingrese contraseña: ")
    if registrar_usuario(usuario, contrasena):
        print("Usuario registrado con éxito.")
    else:
        print("El usuario ya existe.")

    # Verificación
    usuario = input("Ingrese nombre de usuario para verificar: ")
    contrasena = getpass("Ingrese contraseña: ")
    if verificar_contrasena(usuario, contrasena):
        print("Contraseña correcta.")
    else:
        print("Usuario o contraseña incorrectos.")
