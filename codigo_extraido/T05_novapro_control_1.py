import hashlib
import sqlite3

# Función para crear una conexión a la base de datos
def create_connection():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password_hash TEXT)''')
    connection.commit()
    return connection

# Función para hashear una contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para registrar un usuario
def register_user(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (username, password_hash))
        connection.commit()
        print("Usuario registrado exitosamente.")
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    connection.close()

# Función para verificar la contraseña de un usuario
def verify_password(username, password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    connection.close()
    if result and hash_password(password) == result[0]:
        return True
    return False

# Ejemplo de uso
register_user('usuario1', 'contraseña123')
print(verify_password('usuario1', 'contraseña123'))  # Debería imprimir True
print(verify_password('usuario1', 'contraseñaIncorrecta'))  # Debería imprimir False
