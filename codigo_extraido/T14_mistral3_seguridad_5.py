import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
import json
import logging
from urllib.parse import urljoin

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureAPIClient:
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
        ca_bundle_path: Optional[str] = None
    ):
        """
        Cliente seguro para consumir APIs HTTPS.

        Args:
            base_url: URL base de la API (ej: 'https://api.ejemplo.com/v1/')
            token: Token de autenticación (opcional si se pasa en cada request)
            timeout: Timeout en segundos para las requests
            max_retries: Número máximo de reintentos para requests fallidas
            verify_ssl: Verificar certificado SSL (recomendado True)
            ca_bundle_path: Ruta a un bundle de certificados CA personalizado
        """
        if not base_url.startswith(('https://', 'http://')):
            raise ValueError("La URL base debe comenzar con http:// o https://")

        self.base_url = base_url.rstrip('/') + '/'
        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.ca_bundle_path = ca_bundle_path

        # Configurar sesión con reintentos y timeout
        self.session = self._create_session(max_retries)

        # Validar SSL al inicializar
        if self.verify_ssl:
            self._validate_ssl()

    def _create_session(self, max_retries: int) -> requests.Session:
        """Crea una sesión con configuración segura y reintentos."""
        session = requests.Session()

        # Configurar reintentos para requests fallidas
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _validate_ssl(self) -> None:
        """Valida la conexión SSL con el servidor."""
        try:
            response = self.session.get(
                self.base_url,
                timeout=self.timeout,
                verify=self._get_ssl_verification()
            )
            response.raise_for_status()
        except requests.exceptions.SSLError as e:
            logger.error(f"Error de validación SSL: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error al validar conexión con la API: {e}")

    def _get_ssl_verification(self) -> str:
        """Devuelve el parámetro de verificación SSL adecuado."""
        if not self.verify_ssl:
            logger.warning("La verificación SSL está deshabilitada. Esto es inseguro.")
            return False
        return self.ca_bundle_path if self.ca_bundle_path else True

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Construye los headers para la request."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "SecureAPIClient/1.0",
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if custom_headers:
            headers.update(custom_headers)

        return headers

    def _log_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> None:
        """Registra información de la request (sin datos sensibles)."""
        safe_params = {k: "[FILTERED]" if k.lower() in ["password", "token", "secret"] else v
                      for k, v in (params or {}).items()}
        logger.info(f"Request: {method} {endpoint} - Params: {safe_params}")

    def _log_response(self, response: requests.Response) -> None:
        """Registra información de la respuesta."""
        logger.info(f"Response: {response.status_code} - {response.reason}")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta de la API y lanza excepciones si es necesario."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_details = response.json()
            except ValueError:
                error_details = response.text
            logger.error(f"HTTP Error: {e} - Details: {error_details}")
            raise
        except requests.exceptions.JSONDecodeError:
            logger.error("La respuesta no es un JSON válido")
            raise ValueError("La respuesta no es un JSON válido")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la request: {e}")
            raise

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Realiza una request segura a la API.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE, etc.)
            endpoint: Endpoint de la API (ej: 'users')
            params: Parámetros de query string
            data: Datos para enviar en el body (form-encoded)
            json_data: Datos para enviar como JSON en el body
            headers: Headers personalizados
            token: Token de autenticación (sobrescribe el de la instancia)

        Returns:
            Diccionario con la respuesta JSON
        """
        url = urljoin(self.base_url, endpoint)
        auth_token = token if token else self.token

        # Validar que no se envíen ambos tipos de datos
        if data and json_data:
            raise ValueError("No se puede enviar 'data' y 'json_data' simultáneamente")

        # Construir headers
        request_headers = self._get_headers(headers)
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"

        # Registrar request (sin datos sensibles)
        self._log_request(method, endpoint, params)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self._get_ssl_verification()
            )

            self._log_response(response)
            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la request a {url}: {e}")
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una request GET."""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una request POST."""
        return self.request("POST", endpoint, json_data=json_data, **kwargs)

    def put(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza una request PUT."""
        return self.request("PUT", endpoint, json_data=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una request DELETE."""
        return self.request("DELETE", endpoint, **kwargs)

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración segura (en producción, usa variables de entorno)
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.ejemplo.com/v1/")
    API_TOKEN = os.getenv("API_TOKEN", "tu_token_secreto_aqui")

    try:
        # Crear cliente seguro
        client = SecureAPIClient(
            base_url=API_BASE_URL,
            token=API_TOKEN,
            timeout=10,
            max_retries=3,
            verify_ssl=True
        )

        # Ejemplo de request GET
        response = client.get("users", params={"limit": 10})
        print("Respuesta de la API:", json.dumps(response, indent=2))

        # Ejemplo de request POST
        # response = client.post("users", json_data={"name": "Nuevo Usuario"})

    except Exception as e:
        logger.error(f"Error en el cliente API: {e}")
