import datetime

def login(username, password):
    log_message = f"{datetime.datetime.now()} - Intento de inicio de sesión: Usuario={username}, Contraseña={'*' * len(password)}"
    
    with open("login_log.txt", "a") as log_file:
        log_file.write(log_message + "\n")
    
    # Simulación de verificación de credenciales
    valid_username = "usuario1"
    valid_password = "contraseña1"
    
    if username == valid_username and password == valid_password:
        return "Inicio de sesión exitoso"
    else:
        return "Credenciales incorrectas"

# Ejemplo de uso
print(login("usuario1", "contraseña1"))
print(login("usuario2", "contraseña2"))
