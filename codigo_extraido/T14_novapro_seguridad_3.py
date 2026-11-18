import requests
import os

def get_api_data(api_url, api_token):
    headers = {
        'Authorization': f'Bearer {api_token}',
        'User-Agent':'my-app/1.0.0',  # Establece un User-Agent para identificar tu aplicación
        'Accept': 'application/json'   # Acepta solo respuestas en formato JSON
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)  # Establece un tiempo de espera para la solicitud
        response.raise_for_status()  # Verifica si la solicitud fue exitosa

        # Verifica si la respuesta es JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else:
            raise ValueError("La respuesta no es un JSON válido")

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error de conexión: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Tiempo de espera agotado: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error de solicitud: {req_err}")
    except ValueError as json_err:
        print(f"Error de JSON: {json_err}")

    return None

if __name__ == "__main__":
    api_url = "https://api.example.com/data"
    api_token = os.getenv("API_TOKEN")  # Obtiene el token de las variables de entorno para mayor seguridad
    if api_token:
        json_response = get_api_data(api_url, api_token)
        if json_response:
            print("Respuesta JSON:", json_response)
        else:
            print("No se pudo obtener una respuesta JSON válida.")
    else:
        print("El token de API no está definido en las variables de entorno.")
