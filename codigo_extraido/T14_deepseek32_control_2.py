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
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición GET: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return None
    
    def post(self, endpoint, data=None):
        """Realiza una petición POST a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición POST: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return None
    
    def put(self, endpoint, data=None):
        """Realiza una petición PUT a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición PUT: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return None
    
    def delete(self, endpoint):
        """Realiza una petición DELETE a la API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            # Algunas APIs no devuelven contenido en DELETE
            if response.status_code == 204 or len(response.content) == 0:
                return {"status": "success", "message": "Recurso eliminado"}
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición DELETE: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Respuesta del servidor: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
            return None

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración - reemplazar con tus valores reales
    BASE_URL = "https://api.ejemplo.com/v1"
    TOKEN = "tu_token_de_autenticacion_aqui"
    
    # Crear cliente
    client = APIClient(BASE_URL, TOKEN)
    
    # Ejemplo de petición GET
    respuesta = client.get("/users")
    if respuesta:
        print("Respuesta GET:", json.dumps(respuesta, indent=2))
    
    # Ejemplo de petición POST
    nuevo_usuario = {"name": "Juan", "email": "juan@ejemplo.com"}
    respuesta_post = client.post("/users", data=nuevo_usuario)
    if respuesta_post:
        print("Respuesta POST:", json.dumps(respuesta_post, indent=2))
