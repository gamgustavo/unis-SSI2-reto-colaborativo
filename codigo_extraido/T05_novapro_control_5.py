import hashlib
import sqlite3

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect('usuarios.db')
    return conn

# Función para crear la tabla de usuarios si no existe
def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Función para hashear la contraseña
def hashear_password(password):
    salt = 'salt_aleatorio'  # Deberías usar un salt más seguro en producción
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

# Función para registrar un nuevo usuario
def registrar_usuario(nombre, email, password):
    conn = conectar_db()
    cursor = conn.cursor()
    hashed_password = hashear_password(password)
    try:
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, password) VALUES (?,?,?)
        ''', (nombre, email, hashed_password))
        conn.commit()
        print("Usuario registrado con éxito.")
    except sqlite3.IntegrityError:
        print("El email ya está registrado.")
    conn.close()

# Función para verificar la contraseña de un usuario
def verificar_password(email, password):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM usuarios WHERE email =?', (email,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        hashed_password = hashear_password(password)
        return hashed_password == resultado[0]
    return False

# Crear la tabla al iniciar
crear_tabla()
