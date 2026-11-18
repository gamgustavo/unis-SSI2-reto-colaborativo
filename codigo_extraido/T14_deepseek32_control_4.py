import requests
import json

class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            if response.text:
                print(f"Response: {response.text}")
            raise
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            print(f"Timeout Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response text: {response.text}")
            raise
    
    def get(self, endpoint, params=None):
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint, data=None):
        return self._make_request('POST', endpoint, json=data)
    
    def put(self, endpoint, data=None):
        return self._make_request('PUT', endpoint, json=data)
    
    def patch(self, endpoint, data=None):
        return self._make_request('PATCH', endpoint, json=data)
    
    def delete(self, endpoint):
        return self._make_request('DELETE', endpoint)

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    BASE_URL = "https://api.ejemplo.com/v1"
    TOKEN = "tu_token_aqui"
    
    # Crear cliente
    client = APIClient(BASE_URL, TOKEN)
    
    # Ejemplo de solicitud GET
    try:
        response_data = client.get("endpoint")
        print("Respuesta JSON:")
        print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"Error en la solicitud: {e}")
