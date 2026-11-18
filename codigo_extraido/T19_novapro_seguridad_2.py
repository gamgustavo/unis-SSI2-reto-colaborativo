import hashlib
import logging
from datetime import datetime

# Configuración del logger
logging.basicConfig(filename='login_attempts.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def hash_password(password):
    """Hashea una contraseña usando SHA-256."""
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

def login(username, password, stored_credentials):
    """Intenta iniciar sesión y registra el intento."""
    attempt_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    hashed_password = hash_password(password)
    
    logging.info(f"Intento de inicio de sesión: {attempt_time} - Usuario: {username} - Contraseña: {hashed_password}")
    
    if username in stored_credentials and stored_credentials[username] == hashed_password:
        return True
    else:
        return False

# Ejemplo de uso
stored_credentials = {
    'usuario1': hash_password('contraseña1'),
    'usuario2': hash_password('contraseña2')
}

# Intentos de inicio de sesión
print(login('usuario1', 'contraseña1', stored_credentials))  # Debería retornar True
print(login('usuario1', 'contraseña_incorrecta', stored_credentials))  # Debería retornar False
print(login('usuario_inexistente', 'contraseña_cualquiera', stored_credentials))  # Debería retornar False
