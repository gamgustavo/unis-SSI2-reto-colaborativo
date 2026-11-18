import hashlib
import sqlite3

# Función para hashear la contraseña
def hash_password(password):
    salt = 'unique_salt'  # Deberías usar un salt único para cada usuario en producción
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

# Función para registrar un usuario
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY, password TEXT)''')
    
    hashed_password = hash_password(password)
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (username, hashed_password))
    
    conn.commit()
    conn.close()
    print(f"Usuario {username} registrado con éxito.")

# Función para verificar la contraseña de un usuario
def verify_password(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username =?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        stored_password = result[0]
        hashed_password = hash_password(password)
        
        if hashed_password == stored_password:
            return True
        else:
            return False
    else:
        return False

# Ejemplo de uso
register_user('usuario1', 'contraseña123')
print(verify_password('usuario1', 'contraseña123'))  # Debería imprimir True
print(verify_password('usuario1', 'contraseñaIncorrecta'))  # Debería imprimir False
