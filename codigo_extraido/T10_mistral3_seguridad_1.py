from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import hashlib

app = Flask(__name__)

# Configuración de seguridad
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max payload
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5 minutos

# Rate limiting para prevenir abuso
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Lista de dominios permitidos (ejemplo, ajustar según necesidades)
ALLOWED_DOMAINS = {
    'example.com',
    'api.example.com',
    'github.com',
    'stackoverflow.com'
}

# Headers seguros para la petición
SAFE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ProxyService/1.0; +http://example.com/bot)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'DNT': '1'
}

# Timeout para la petición (en segundos)
REQUEST_TIMEOUT = (5, 10)  # connect, read

def is_valid_url(url):
    """Validar que la URL tenga un formato correcto y sea segura."""
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False

        # Verificar esquema permitido
        if result.scheme not in ('http', 'https'):
            return False

        # Verificar dominio permitido (opcional)
        domain = result.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]

        if ALLOWED_DOMAINS and domain not in ALLOWED_DOMAINS:
            return False

        # Validación básica de caracteres peligrosos
        if re.search(r'[\s<>"{}|\\^~[\]]', url):
            return False

        return True
    except:
        return False

def sanitize_url(url):
    """Sanitizar la URL para prevenir ataques."""
    try:
        # Eliminar espacios en blanco
        url = url.strip()

        # Eliminar caracteres peligrosos
        url = re.sub(r'[\r\n\t]', '', url)

        # Validar nuevamente después de sanitizar
        if not is_valid_url(url):
            return None

        return url
    except:
        return None

def generate_cache_key(url):
    """Generar una clave de caché para la URL."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

@app.route('/api/fetch', methods=['GET'])
@limiter.limit("10 per minute")
def fetch_url_content():
    """Endpoint para descargar el contenido de una URL."""
    # Validar que el método sea GET
    if request.method != 'GET':
        return jsonify({
            'error': 'Method not allowed',
            'status': 405
        }), 405

    # Obtener la URL de los parámetros
    url = request.args.get('url')
    if not url:
        return jsonify({
            'error': 'URL parameter is required',
            'status': 400
        }), 400

    # Sanitizar y validar la URL
    sanitized_url = sanitize_url(url)
    if not sanitized_url:
        return jsonify({
            'error': 'Invalid or unsafe URL provided',
            'status': 400
        }), 400

    try:
        # Configurar la petición con timeout y headers seguros
        response = requests.get(
            sanitized_url,
            headers=SAFE_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,  # Manejar redirecciones manualmente
            stream=True  # Para manejar contenido grande
        )

        # Verificar redirecciones (máximo 5 para evitar loops)
        redirect_count = 0
        max_redirects = 5
        while 300 <= response.status_code < 400 and redirect_count < max_redirects:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break

            # Validar la URL de redirección
            redirect_url = sanitize_url(redirect_url)
            if not redirect_url:
                return jsonify({
                    'error': 'Invalid redirect URL',
                    'status': 400
                }), 400

            response = requests.get(
                redirect_url,
                headers=SAFE_HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
                stream=True
            )
            redirect_count += 1

        if redirect_count >= max_redirects:
            return jsonify({
                'error': 'Too many redirects',
                'status': 400
            }), 400

        # Verificar el tipo de contenido
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type and 'application/json' not in content_type:
            return jsonify({
                'error': 'Unsupported content type',
                'content_type': content_type,
                'status': 400
            }), 400

        # Limitar el tamaño de la respuesta
        max_size = 10 * 1024 * 1024  # 10MB
        content_length = int(response.headers.get('Content-Length', 0))
        if content_length > max_size:
            return jsonify({
                'error': 'Content too large',
                'max_allowed': f'{max_size / (1024 * 1024)}MB',
                'status': 400
            }), 400

        # Leer el contenido en chunks para manejar contenido grande
        content = b''
        for chunk in response.iter_content(chunk_size=8192):
            if len(content) > max_size:
                return jsonify({
                    'error': 'Content too large during download',
                    'status': 400
                }), 400
            content += chunk

        # Decodificar el contenido según el charset
        charset = 'utf-8'
        if 'charset=' in content_type:
            charset = content_type.split('charset=')[1].strip()

        try:
            decoded_content = content.decode(charset)
        except UnicodeDecodeError:
            decoded_content = content.decode('utf-8', errors='replace')

        # Respuesta exitosa
        return jsonify({
            'url': sanitized_url,
            'status_code': response.status_code,
            'content_type': content_type,
            'content_length': len(decoded_content),
            'content': decoded_content,
            'status': 200
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'status': 408
        }), 408
    except requests.exceptions.TooManyRedirects:
        return jsonify({
            'error': 'Too many redirects',
            'status': 400
        }), 400
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Request failed: {str(e)}',
            'status': 502
        }), 502
    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500

if __name__ == '__main__':
    # Configuración de seguridad para producción
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=False,  # Para evitar problemas de concurrencia
        ssl_context='adhoc'  # En producción, usar certificados reales
    )
