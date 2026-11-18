from flask import Flask, request, jsonify, abort
import requests
from urllib.parse import urlparse
import re
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuración de seguridad
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,
    PREFERRED_URL_SCHEME='https'
)

# Lista blanca de dominios permitidos (ajusta según tus necesidades)
ALLOWED_DOMAINS = {
    'example.com',
    'trusted-site.org'
}

# Tamaño máximo de respuesta permitido (en bytes)
MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB

# User-Agent personalizado para evitar bloqueos
USER_AGENT = 'Mozilla/5.0 (compatible; ProxyService/1.0; +http://yoursite.com/bot)'

# Timeout para las peticiones (en segundos)
REQUEST_TIMEOUT = (5, 10)  # connect, read

def is_valid_url(url):
    """Validar la estructura de la URL y el dominio permitido."""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False

        # Verificar esquema permitido
        if parsed.scheme not in ('http', 'https'):
            return False

        # Verificar dominio permitido
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]

        if domain not in ALLOWED_DOMAINS:
            return False

        # Validación adicional con regex
        pattern = re.compile(
            r'^(https?://)?'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(pattern, url) is not None

    except:
        return False

def sanitize_headers(headers):
    """Sanitizar headers para evitar inyección de headers maliciosos."""
    safe_headers = {}
    if not headers:
        return safe_headers

    # Headers permitidos
    allowed_headers = {
        'accept', 'accept-encoding', 'accept-language',
        'cache-control', 'connection', 'dnt', 'host',
        'upgrade-insecure-requests', 'user-agent'
    }

    for key, value in headers.items():
        if key.lower() in allowed_headers:
            safe_headers[key] = str(value)

    return safe_headers

@app.route('/fetch', methods=['GET'])
def fetch_url():
    """Endpoint para descargar contenido de una URL."""
    # Verificar Content-Type para prevenir CSRF
    if not request.headers.get('Content-Type', '').startswith('application/json'):
        if request.method == 'GET':
            # Para GET, verificamos el Accept header
            if 'application/json' not in request.headers.get('Accept', ''):
                abort(400, description="Invalid Accept header")

    # Obtener la URL de los parámetros
    url = request.args.get('url')
    if not url:
        abort(400, description="URL parameter is required")

    # Validar la URL
    if not is_valid_url(url):
        abort(400, description="Invalid or not allowed URL")

    try:
        # Configurar headers para la petición
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Añadir headers sanitizados del cliente
        client_headers = sanitize_headers(dict(request.headers))
        headers.update(client_headers)

        # Realizar la petición con timeout y manejo de redirecciones
        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            stream=True  # Para manejar respuestas grandes
        )

        # Verificar el tamaño de la respuesta
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > MAX_RESPONSE_SIZE:
            abort(413, description="Response too large")

        # Verificar el tipo de contenido
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type and 'text/plain' not in content_type:
            abort(400, description="Only text content is allowed")

        # Leer la respuesta en chunks para evitar consumo excesivo de memoria
        content = []
        size = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                size += len(chunk)
                if size > MAX_RESPONSE_SIZE:
                    abort(413, description="Response too large")
                content.append(chunk)

        content = b''.join(content).decode('utf-8', errors='replace')

        # Sanitizar el contenido (eliminar scripts potencialmente peligrosos)
        # Nota: Esto es básico, para producción considera usar una librería como bleach
        sanitized_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', content, flags=re.IGNORECASE)

        return jsonify({
            'url': url,
            'content': sanitized_content,
            'status_code': response.status_code,
            'headers': dict(response.headers)
        })

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching URL {url}: {str(e)}")
        abort(502, description="Error fetching the requested URL")
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        abort(500, description="Internal server error")

# Manejo de errores personalizado
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(413)
@app.errorhandler(500)
@app.errorhandler(502)
def handle_error(e):
    response = jsonify({
        'error': str(e.description),
        'status_code': e.code
    })
    response.status_code = e.code
    return response

if __name__ == '__main__':
    # Configuración para producción (usar un servidor WSGI en producción)
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
