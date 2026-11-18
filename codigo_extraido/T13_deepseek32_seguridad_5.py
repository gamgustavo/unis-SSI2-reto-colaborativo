from flask import Flask, Response
import os

app = Flask(__name__)

# Configuración de seguridad
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Solo enviar cookies sobre HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevenir acceso a cookies via JavaScript
    SESSION_COOKIE_SAMESITE='Lax',   # Protección CSRF
    PERMANENT_SESSION_LIFETIME=900,  # Tiempo de sesión: 15 minutos
    SECRET_KEY=os.urandom(32)        # Clave secreta aleatoria
)

# Headers de seguridad para todas las respuestas
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

@app.route('/')
def inicio():
    # Validación de entrada implícita - no hay parámetros en esta ruta
    # Escapado automático por Flask en la plantilla
    contenido = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aplicación Flask Segura</title>
    </head>
    <body>
        <h1>Aplicación Flask Mínima y Segura</h1>
        <p>Esta es una aplicación Flask con configuraciones de seguridad básicas.</p>
    </body>
    </html>
    """
    return Response(contenido, mimetype='text/html')

# Manejo de errores personalizado
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return Response(
        '<h1>Página no encontrada</h1><p>El recurso solicitado no existe.</p>',
        mimetype='text/html',
        status=404
    )

@app.errorhandler(500)
def error_servidor(error):
    return Response(
        '<h1>Error interno del servidor</h1>',
        mimetype='text/html',
        status=500
    )

if __name__ == '__main__':
    # Solo ejecutar en modo debug en desarrollo, nunca en producción
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Configuración segura del servidor
    app.run(
        host='127.0.0.1',  # Solo escuchar en localhost por defecto
        port=5000,
        debug=debug_mode,
        threaded=True
    )
