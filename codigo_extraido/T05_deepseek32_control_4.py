import sqlite3
import hashlib
import secrets
import string

def crear_tabla_usuarios():
    """Crea la tabla de usuarios si no existe"""
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generar_salt(longitud=16):
    """Genera un salt aleatorio"""
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

def hash_password(password, salt):
    """Genera el hash de la contraseña usando SHA-256"""
    password_salt = password + salt
    return hashlib.sha256(password_salt.encode()).hexdigest()

def registrar_usuario(username, password):
    """
    Registra un nuevo usuario en la base de datos
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
    
    Returns:
        bool: True si el registro fue exitoso, False si el usuario ya existe
    """
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Generar salt y hash de la contraseña
        salt = generar_salt()
        password_hash = hash_password(password, salt)
        
        # Insertar el nuevo usuario
        cursor.execute(
            "INSERT INTO usuarios (username, salt, password_hash) VALUES (?, ?, ?)",
            (username, salt, password_hash)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return False

def verificar_usuario(username, password):
    """
    Verifica las credenciales de un usuario
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano a verificar
    
    Returns:
        bool: True si las credenciales son correctas, False en caso contrario
    """
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        # Obtener el salt y hash almacenados
        cursor.execute(
            "SELECT salt, password_hash FROM usuarios WHERE username = ?",
            (username,)
        )
        
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            return False
        
        salt_almacenado, hash_almacenado = resultado
        
        # Calcular el hash de la contraseña proporcionada con el salt almacenado
        hash_calculado = hash_password(password, salt_almacenado)
        
        # Comparar los hashes de manera segura (comparación constante en tiempo)
        return secrets.compare_digest(hash_calculado, hash_almacenado)
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return False

def cambiar_password(username, old_password, new_password):
    """
    Cambia la contraseña de un usuario
    
    Args:
        username: Nombre de usuario
        old_password: Contraseña actual
        new_password: Nueva contraseña
    
    Returns:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    # Verificar la contraseña actual primero
    if not verificar_usuario(username, old_password):
        return False
    
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        # Generar nuevo salt y hash
        nuevo_salt = generar_salt()
        nuevo_hash = hash_password(new_password, nuevo_salt)
        
        # Actualizar en la base de datos
        cursor.execute(
            "UPDATE usuarios SET salt = ?, password_hash = ? WHERE username = ?",
            (nuevo_salt, nuevo_hash, username)
        )
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return False

# Crear la tabla al importar el módulo
crear_tabla_usuarios()

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de registro
    if registrar_usuario("usuario_ejemplo", "MiContraseñaSegura123"):
        print("Usuario registrado exitosamente")
    else:
        print("El usuario ya existe")
    
    # Ejemplo de verificación
    if verificar_usuario("usuario_ejemplo", "MiContraseñaSegura123"):
        print("Credenciales correctas")
    else:
        print("Credenciales incorrectas")
    
    # Ejemplo de cambio de contraseña
    if cambiar_password("usuario_ejemplo", "MiContraseñaSegura123", "NuevaContraseña456"):
        print("Contraseña cambiada exitosamente")
    else:
        print("Error al cambiar la contraseña")
