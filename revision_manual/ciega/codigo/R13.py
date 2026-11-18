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
    SECRET_KEY='tu_clave_secreta_aqui_cambiala_por_una_aleatoria_y_segura'  # Cambia esto en producción
)

# Plantilla HTML segura con CSP
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'">
    <title>Comentarios Seguros</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .comment { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Deja tu comentario</h1>
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    <form method="POST" action="/">
        <textarea name="comment" rows="4" cols="50" required maxlength="500" placeholder="Escribe tu comentario aquí..."></textarea><br>
        <button type="submit">Enviar comentario</button>
    </form>

    {% if comments %}
        <h2>Comentarios recientes</h2>
        {% for comment in comments %}
            <div class="comment">{{ comment|safe }}</div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

# Lista para almacenar comentarios (en producción usa una base de datos segura)
comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    sanitized_comment = None

    if request.method == 'POST':
        # Validación CSRF (en producción usa Flask-WTF o similar)
        if not validate_csrf(request):
            return "Error de seguridad: Token CSRF inválido", 403

        # Obtener y validar el comentario
        raw_comment = request.form.get('comment', '').strip()

        if not raw_comment:
            error = "El comentario no puede estar vacío"
        elif len(raw_comment) > 500:
            error = "El comentario es demasiado largo (máximo 500 caracteres)"
        else:
            # Sanitización del comentario
            sanitized_comment = sanitize_comment(raw_comment)
            comments.append(sanitized_comment)

    # Mostrar solo los últimos 10 comentarios
    recent_comments = comments[-10:]

    return render_template_string(
        HTML_TEMPLATE,
        comments=recent_comments,
        error=error
    )

def sanitize_comment(comment):
    """Sanitiza el comentario para prevenir XSS y otros ataques"""
    # Permitir solo etiquetas básicas y atributos seguros
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a']
    allowed_attrs = {'a': ['href', 'title']}

    # Limpiar el comentario con bleach
    cleaned = bleach.clean(
        comment,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

    # Escapar caracteres especiales y permitir solo URLs seguras
    cleaned = bleach.linkify(cleaned, callbacks=[lambda attrs, new: None if not attrs['href'].startswith(('http://', 'https://')) else attrs])

    return Markup(cleaned)

def validate_csrf(request):
    """Validación básica de CSRF (en producción usa Flask-WTF)"""
    # En una implementación real, compararías con un token almacenado en la sesión
    return True  # Simplificado para este ejemplo

if __name__ == '__main__':
    # Configuración de seguridad para el servidor de desarrollo
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context='adhoc',  # Usa certificados reales en producción
        debug=False  # Nunca uses debug=True en producción
    )
