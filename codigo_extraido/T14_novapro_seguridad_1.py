import requests
import os

def obtener_token():
    # Obtiene el token de una variable de entorno para mayor seguridad
    return os.getenv('API_TOKEN')

def consumir_api(url):
    token = obtener_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'MiCliente/1.0',  # Identifica tu cliente para mejorar el rastreo y la depuración
        'Accept': 'application/json'   # Especifica que esperas una respuesta JSON
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)  # Establece un tiempo de espera razonable
        response.raise_for_status()  # Verifica si la respuesta contiene un código de error HTTP
        return response.json()  # Devuelve el contenido JSON de la respuesta
    except requests.RequestException as e:
        print(f"Ocurrió un error al consumir la API: {e}")
        return None

# Uso de la función
url_api = 'https://api.ejemplo.com/datos'
respuesta = consumir_api(url_api)
if respuesta:
    print(respuesta)
