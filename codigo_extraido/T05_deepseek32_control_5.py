import sqlite3
import hashlib
import secrets

def crear_tabla_usuarios():
    """Crea la tabla de usuarios si no existe"""
    conexion = sqlite3.connect('usuarios.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    conexion.commit()
    conexion.close()

def generar_salt():
    """Genera un salt aleatorio para cada usuario"""
    return secrets.token_hex(16)

def hash_password(password, salt):
    """Genera el hash de la contraseña usando SHA-256 y salt"""
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()

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
        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute('SELECT username FROM usuarios WHERE username = ?', (username,))
        if cursor.fetchone():
            conexion.close()
            return False
        
        # Generar salt y hash de la contraseña
        salt = generar_salt()
        password_hash = hash_password(password, salt)
        
        # Insertar el nuevo usuario
        cursor.execute(
            'INSERT INTO usuarios (username, salt, password_hash) VALUES (?, ?, ?)',
            (username, salt, password_hash)
        )
        
        conexion.commit()
        conexion.close()
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
        conexion = sqlite3.connect('usuarios.db')
        cursor = conexion.cursor()
        
        # Obtener el salt y hash almacenados
        cursor.execute(
            'SELECT salt, password_hash FROM usuarios WHERE username = ?',
            (username,)
        )
        
        resultado = cursor.fetchone()
        conexion.close()
        
        if not resultado:
            return False
        
        salt_almacenado, hash_almacenado = resultado
        
        # Calcular el hash de la contraseña proporcionada
        hash_calculado = hash_password(password, salt_almacenado)
        
        # Comparar los hashes de manera segura
        return secrets.compare_digest(hash_almacenado, hash_calculado)
        
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return False

# Crear la tabla al importar el módulo
crear_tabla_usuarios()

# Ejemplo de uso
if __name__ == "__main__":
    # Registrar un usuario
    if registrar_usuario("usuario_ejemplo", "mi_contraseña_segura"):
        print("Usuario registrado exitosamente")
    else:
        print("El usuario ya existe")
    
    # Verificar credenciales
    if verificar_usuario("usuario_ejemplo", "mi_contraseña_segura"):
        print("Credenciales correctas")
    else:
        print("Credenciales incorrectas")
    
    # Verificar credenciales incorrectas
    if verificar_usuario("usuario_ejemplo", "contraseña_equivocada"):
        print("Credenciales correctas")
    else:
        print("Credenciales incorrectas (esperado)")
