import requests
import json

class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })
    
    def get(self, endpoint, params=None):
        """Realiza una petición GET a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error de conexión: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout: {timeout_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
            raise
        except json.JSONDecodeError as json_err:
            print(f"Error decodificando JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
            raise
    
    def post(self, endpoint, data=None):
        """Realiza una petición POST a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
            raise
        except json.JSONDecodeError as json_err:
            print(f"Error decodificando JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
            raise
    
    def put(self, endpoint, data=None):
        """Realiza una petición PUT a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
            raise
        except json.JSONDecodeError as json_err:
            print(f"Error decodificando JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
            raise
    
    def delete(self, endpoint):
        """Realiza una petición DELETE a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            # Algunas APIs no devuelven contenido en DELETE
            if response.text:
                return response.json()
            return {"status": "success", "message": "Recurso eliminado"}
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Error en la petición: {req_err}")
            raise
        except json.JSONDecodeError as json_err:
            print(f"Error decodificando JSON: {json_err}")
            print(f"Respuesta cruda: {response.text}")
            raise

# Ejemplo de uso:
if __name__ == "__main__":
    # Configuración
    BASE_URL = "https://api.ejemplo.com/v1"
    TOKEN = "tu_token_aqui"
    
    # Crear cliente
    client = APIClient(BASE_URL, TOKEN)
    
    # Ejemplo de petición GET
    try:
        datos = client.get("/recursos")
        print("Respuesta GET:", json.dumps(datos, indent=2))
    except Exception as e:
        print(f"Error en GET: {e}")
    
    # Ejemplo de petición POST
    try:
        nuevo_recurso = {"nombre": "Ejemplo", "valor": 123}
        respuesta_post = client.post("/recursos", data=nuevo_recurso)
        print("Respuesta POST:", json.dumps(respuesta_post, indent=2))
    except Exception as e:
        print(f"Error en POST: {e}")
