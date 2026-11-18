import logging
from datetime import datetime

def login(username, password):
    """
    Función de inicio de sesión que registra cada intento en un archivo de log.
    
    Args:
        username (str): Nombre de usuario proporcionado
        password (str): Contraseña proporcionada
    
    Returns:
        bool: Siempre retorna False (solo para demostración del logging)
    """
    # Configurar el sistema de logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('login_attempts.log', encoding='utf-8'),
            logging.StreamHandler()  # También muestra en consola
        ]
    )
    
    # Registrar el intento de inicio de sesión
    # En un caso real, aquí iría la lógica de autenticación
    logging.info(f"Intento de login - Usuario: {username}, Contraseña: {password}")
    
    # Retornar False para esta implementación de ejemplo
    # En una implementación real, aquí se verificarían las credenciales
    return False

# Ejemplo de uso
if __name__ == "__main__":
    # Simular algunos intentos de login
    login("usuario1", "clave123")
    login("admin", "password123")
    login("test_user", "test_pass")
