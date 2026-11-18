import requests

def consumir_api(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al consumir la API: {e}")
        return None

# Ejemplo de uso:
# url = "https://api.ejemplo.com/recurso"
# token = "tu_token_aqui"
# resultado = consumir_api(url, token)
# print(resultado)
