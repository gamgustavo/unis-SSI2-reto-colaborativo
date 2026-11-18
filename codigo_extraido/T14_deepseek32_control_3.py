import requests
import json

class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get(self, endpoint, params=None):
        """Realiza una petición GET a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params,
                verify=True  # Verificar certificados SSL
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error de conexión: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
        except json.JSONDecodeError as json_err:
            print(f"Error al decodificar JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
        return None
    
    def post(self, endpoint, data=None):
        """Realiza una petición POST a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=data,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error de conexión: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
        except json.JSONDecodeError as json_err:
            print(f"Error al decodificar JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración - reemplazar con tus valores reales
    BASE_URL = "https://api.ejemplo.com/v1"
    TOKEN = "tu_token_de_autenticacion_aqui"
    
    # Crear cliente
    client = APIClient(BASE_URL, TOKEN)
    
    # Ejemplo de petición GET
    print("Realizando petición GET...")
    resultado_get = client.get("recursos", params={"limit": 10})
    if resultado_get:
        print("Respuesta GET:")
        print(json.dumps(resultado_get, indent=2))
    
    # Ejemplo de petición POST
    print("\nRealizando petición POST...")
    datos_post = {
        "nombre": "Ejemplo",
        "valor": 123
    }
    resultado_post = client.post("recursos", data=datos_post)
    if resultado_post:
        print("Respuesta POST:")
        print(json.dumps(resultado_post, indent=2))
