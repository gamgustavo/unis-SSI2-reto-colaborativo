import os
import platform

def ping_host(hostname):
    # Determina el parámetro de ping según el sistema operativo
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '4'  # Número de pings a enviar

    # Construye el comando de ping
    command = ['ping', param, count, hostname]

    # Ejecuta el comando y captura la respuesta
    response = os.system(' '.join(command))

    # Verifica si el host respondió
    if response == 0:
        print(f"El host {hostname} está respondiendo.")
    else:
        print(f"El host {hostname} no responde.")

if __name__ == "__main__":
    host = input("Introduce el nombre del host o dirección IP: ")
    ping_host(host)
