from flask import Flask, request, render_template_string, escape
from markupsafe import Markup
import bleach

app = Flask(__name__)

# Configuración de seguridad
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutos
    SECRET_KEY='tu_clave_secreta_aqui_cambiala_por_una_aleatoria_y_larga'  # Cambia esto en producción
)

# Plantilla HTML segura con CSP
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy"
          content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'">
    <title>Comentarios Seguros</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .comment { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        textarea { width: 100%; padding: 10px; margin: 10px 0; }
        button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>Deja tu comentario</h1>
    <form method="POST" action="/">
        <textarea name="comment" rows="4" required maxlength="500"
                  placeholder="Escribe tu comentario aquí (máximo 500 caracteres)"></textarea>
        <button type="submit">Enviar comentario</button>
    </form>

    {% if comments %}
    <h2>Comentarios recientes</h2>
    {% for comment in comments %}
    <div class="comment">
        <p>{{ comment|safe }}</p>
    </div>
    {% endfor %}
    {% endif %}
</body>
</html>
"""

# Lista para almacenar comentarios (en producción usa una base de datos)
comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validación CSRF (en producción usa Flask-WTF o similar)
        if not validate_csrf(request.form.get('csrf_token')):
            return "Token CSRF inválido", 403

        # Obtener y limpiar el comentario
        raw_comment = request.form.get('comment', '').strip()

        # Validación de longitud
        if not raw_comment or len(raw_comment) > 500:
            return "Comentario inválido", 400

        # Sanitización con bleach
        clean_comment = bleach.clean(
            raw_comment,
            tags=[],  # No permitir ninguna etiqueta HTML
            attributes={},
            styles=[],
            strip=True,
            strip_comments=True
        )

        # Escapar el comentario para evitar XSS
        escaped_comment = escape(clean_comment)

        # Convertir saltos de línea a <br> para mejor visualización
        formatted_comment = Markup(escaped_comment.replace('\n', '<br>'))

        # Almacenar el comentario (en producción usa una base de datos)
        comments.append(formatted_comment)

        # Limitar el número de comentarios almacenados
        if len(comments) > 20:
            comments.pop(0)

    # Generar token CSRF para el formulario
    csrf_token = generate_csrf_token()

    return render_template_string(
        HTML_TEMPLATE,
        comments=comments,
        csrf_token=csrf_token
    )

def generate_csrf_token():
    """Genera un token CSRF simple (en producción usa Flask-WTF)"""
    if 'csrf_token' not in app.config:
        import secrets
        app.config['csrf_token'] = secrets.token_hex(16)
    return app.config['csrf_token']

def validate_csrf(token):
    """Valida el token CSRF"""
    if not token:
        return False
    return token == app.config.get('csrf_token')

if __name__ == '__main__':
    # Configuración para producción (usa un servidor WSGI en producción)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Nunca habilites debug en producción
        ssl_context='adhoc'  # En producción usa certificados SSL reales
    )
