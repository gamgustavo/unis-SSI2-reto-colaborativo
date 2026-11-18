import datetime

def login(username, password):
    log_message = f"{datetime.datetime.now()} - Intento de inicio de sesión: Usuario={username}, Contraseña={'*' * len(password)}"
    with open("login_log.txt", "a") as log_file:
        log_file.write(log_message + "\n")
    # Simulación de verificación de credenciales
    if username == "usuario" and password == "contraseña":
        return "Inicio de sesión exitoso"
    else:
        return "Credenciales incorrectas"

# Ejemplo de uso
# print(login("usuario", "contraseña"))
# print(login("otro_usuario", "otra_contraseña"))
