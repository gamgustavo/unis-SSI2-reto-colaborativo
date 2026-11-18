import hashlib
import sqlite3

# Configuración de la base de datos
DATABASE = 'users.db'

def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password_hash TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(str(len(password)).encode()).hexdigest().encode()
    password, salt = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt + password

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by the user"""
    salt = stored_password[:16]
    stored_password = stored_password[16:]
    return hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000) == stored_password

def register_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (username, password_hash))
        conn.commit()
        print("Usuario registrado exitosamente.")
    except sqlite3.IntegrityError:
        print("El usuario ya existe.")
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and verify_password(result[0], password):
        print("Contraseña verificada exitosamente.")
        return True
    else:
        print("Nombre de usuario o contraseña incorrectos.")
        return False

# Configurar la base de datos al iniciar
setup_database()

# Ejemplo de uso
register_user('usuario1', 'contraseña123')
verify_user('usuario1', 'contraseña123')
verify_user('usuario1', 'contraseñaIncorrecta')
