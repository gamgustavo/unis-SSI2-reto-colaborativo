from flask import Flask, request, render_template_string, escape
import bleach

app = Flask(__name__)

# Configuración de seguridad
app.config.update(
    SECRET_KEY='tu_clave_secreta_aqui_cambiala_por_una_aleatoria_y_segura',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,  # Habilitar solo si usas HTTPS
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutos
    SESSION_COOKIE_SAMESITE='Lax'
)

# Plantilla HTML segura con CSP y otras protecciones
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy"
          content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'">
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
        <textarea name="comment" rows="4" cols="50" required
                  placeholder="Escribe tu comentario aquí..."></textarea><br>
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

# Lista para almacenar comentarios (en producción usar una base de datos segura)
comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        # Validación del contenido
        if 'comment' not in request.form:
            error = "El comentario es obligatorio"
        else:
            # Sanitización del input
            raw_comment = request.form['comment']

            # Validación de longitud
            if len(raw_comment) > 1000:
                error = "El comentario es demasiado largo (máximo 1000 caracteres)"
            elif len(raw_comment.strip()) == 0:
                error = "El comentario no puede estar vacío"
            else:
                # Sanitización con bleach (permite solo algunos tags y atributos)
                clean_comment = bleach.clean(
                    raw_comment,
                    tags=['p', 'br', 'b', 'i', 'u', 'em', 'strong', 'a'],
                    attributes={'a': ['href', 'title']},
                    styles=[],
                    strip=True,
                    strip_comments=True
                )

                # Escapar caracteres especiales para evitar XSS
                escaped_comment = escape(clean_comment)

                # Validación adicional para URLs en enlaces
                if '<a' in escaped_comment.lower():
                    # Verificar que los enlaces sean seguros
                    if not all(
                        href.startswith(('http://', 'https://')) and
                        not href.startswith(('javascript:', 'data:'))
                        for href in bleach.linkify(escaped_comment)
                    ):
                        error = "Los enlaces deben ser URLs HTTP/HTTPS válidas"
                    else:
                        comments.append(escaped_comment)
                else:
                    comments.append(escaped_comment)

    # Limitar la cantidad de comentarios mostrados
    displayed_comments = comments[-10:] if comments else []

    return render_template_string(
        HTML_TEMPLATE,
        comments=displayed_comments,
        error=error
    )

if __name__ == '__main__':
    # Configuración para producción (usar un servidor WSGI en producción)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Nunca habilitar debug en producción
        ssl_context='adhoc'  # En producción usar un certificado SSL válido
    )
