import os
from flask import Flask, jsonify
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Configuración segura
app.config.update(
    SECRET_KEY=os.urandom(24),  # Clave secreta aleatoria para sesiones
    SESSION_COOKIE_SECURE=True,  # Solo enviar cookies sobre HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Evitar acceso a cookies desde JavaScript
    SESSION_COOKIE_SAMESITE='Lax',  # Protección CSRF básica
    PERMANENT_SESSION_LIFETIME=1800,  # Sesiones expiran en 30 minutos
)

# Middleware para seguridad en producción
if not app.debug:
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", "cdn.example.com"],
            'style-src': ["'self'", "'unsafe-inline'", "cdn.example.com"],
            'img-src': ["'self'", "data:", "cdn.example.com"],
        }
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

@app.route('/')
def home():
    """Ruta de inicio segura."""
    return jsonify({
        'status': 'success',
        'message': 'Bienvenido a la aplicación Flask segura',
        'version': '1.0.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Manejo seguro de errores 404."""
    return jsonify({'status': 'error', 'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo seguro de errores 500."""
    app.logger.error(f'Error interno: {error}')
    return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Configuración para ejecución segura
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        ssl_context='adhoc' if app.debug else None,  # HTTPS en desarrollo con certificado ad-hoc
        debug=False  # Nunca habilitar debug en producción
    )
