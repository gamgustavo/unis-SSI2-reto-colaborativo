import datetime

def login(usuario, contraseña):
    with open("log.txt", "a") as log_file:
        intento = f"{datetime.datetime.now()} - Usuario: {usuario}, Contraseña: {contraseña}\n"
        log_file.write(intento)
        print("Intento de inicio de sesión registrado.")

# Ejemplo de uso
# login("usuario1", "contraseña123")
