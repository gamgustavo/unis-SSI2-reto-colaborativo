import requests
import json

class APIClient:
    def __init__(self, base_url, token):
        """
        Inicializa el cliente API con la URL base y el token de autenticación.
        
        Args:
            base_url (str): URL base de la API
            token (str): Token de autenticación
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get(self, endpoint, params=None):
        """
        Realiza una petición GET a la API.
        
        Args:
            endpoint (str): Endpoint de la API (sin la URL base)
            params (dict, optional): Parámetros de consulta
            
        Returns:
            dict: Respuesta JSON de la API
            
        Raises:
            requests.exceptions.RequestException: Si ocurre un error en la petición
            ValueError: Si la respuesta no es JSON válido
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta del servidor: {response.text}")
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
            print(f"Respuesta recibida: {response.text}")
            raise ValueError("La respuesta no es un JSON válido")
    
    def post(self, endpoint, data=None):
        """
        Realiza una petición POST a la API.
        
        Args:
            endpoint (str): Endpoint de la API (sin la URL base)
            data (dict, optional): Datos a enviar en el cuerpo de la petición
            
        Returns:
            dict: Respuesta JSON de la API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Error HTTP: {http_err}")
            if response.text:
                print(f"Respuesta del servidor: {response.text}")
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
            print(f"Respuesta recibida: {response.text}")
            raise ValueError("La respuesta no es un JSON válido")

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración - reemplazar con tus valores reales
    BASE_URL = "https://api.ejemplo.com/v1"
    TOKEN = "tu_token_de_autenticacion_aqui"
    
    # Crear instancia del cliente
    client = APIClient(BASE_URL, TOKEN)
    
    try:
        # Ejemplo de petición GET
        print("Realizando petición GET...")
        response_get = client.get("/users", params={"limit": 10})
        print(f"Respuesta GET: {json.dumps(response_get, indent=2)}")
        
        # Ejemplo de petición POST
        print("\nRealizando petición POST...")
        new_user = {
            "name": "Juan Pérez",
            "email": "juan@ejemplo.com"
        }
        response_post = client.post("/users", data=new_user)
        print(f"Respuesta POST: {json.dumps(response_post, indent=2)}")
        
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
