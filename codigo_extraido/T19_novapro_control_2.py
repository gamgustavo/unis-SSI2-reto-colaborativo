import datetime

def login(username, password):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - Intento de inicio de sesión: Usuario={username}, Contraseña={password}\n"
    
    with open("login_attempts.log", "a") as log_file:
        log_file.write(log_message)

    # Simulación de verificación de credenciales (solo para ejemplo)
    valid_username = "usuario1"
    valid_password = "contraseña1"
    
    if username == valid_username and password == valid_password:
        return "Inicio de sesión exitoso"
    else:
        return "Credenciales incorrectas"

# Ejemplo de uso
print(login("usuario1", "contraseña1"))
print(login("usuario2", "contraseña2"))
