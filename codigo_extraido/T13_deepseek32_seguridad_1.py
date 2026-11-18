from flask import Flask, Response
import os

app = Flask(__name__)

# Configuración de seguridad básica
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Solo enviar cookies sobre HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevenir acceso a cookies via JavaScript
    SESSION_COOKIE_SAMESITE='Lax',   # Protección CSRF
    PERMANENT_SESSION_LIFETIME=900,  # Tiempo de sesión: 15 minutos
)

# Headers de seguridad HTTP
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

@app.route('/')
def home():
    # Validación de entrada implícita - no hay parámetros en esta ruta
    # Respuesta segura con Content-Type explícito
    return Response(
        '<h1>¡Hola! Esta es una aplicación Flask segura.</h1>'
        '<p>Implementa buenas prácticas de seguridad OWASP.</p>',
        mimetype='text/html',
        headers={'Cache-Control': 'no-store, max-age=0'}  # Prevenir caching sensible
    )

# Manejo de errores personalizado para evitar fugas de información
@app.errorhandler(404)
def page_not_found(e):
    return Response(
        '<h1>Página no encontrada</h1>',
        status=404,
        mimetype='text/html'
    )

@app.errorhandler(500)
def internal_server_error(e):
    return Response(
        '<h1>Error interno del servidor</h1>',
        status=500,
        mimetype='text/html'
    )

if __name__ == '__main__':
    # Configuración segura del servidor de desarrollo
    # En producción, usar un servidor WSGI como Gunicorn detrás de un proxy inverso
    port = int(os.environ.get('PORT', 5000))
    
    # IMPORTANTE: En producción, usar HTTPS y deshabilitar debug
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        # En producción, estas opciones deben manejarse en el servidor WSGI/proxy
        ssl_context='adhoc' if debug_mode else None  # Solo para desarrollo
    )
