from flask import Flask, request, render_template_string, escape
import html

app = Flask(__name__)

# Plantilla HTML segura con escape automático en la plantilla
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comentarios Seguros</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        form {
            margin-bottom: 30px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .comment {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
            border-radius: 5px;
            word-wrap: break-word;
        }
        .comment-meta {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .no-comments {
            color: #888;
            font-style: italic;
        }
        .error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Comentarios Seguros</h1>
        
        <form method="POST" action="/">
            <label for="comment">Escribe tu comentario:</label><br>
            <textarea id="comment" name="comment" required 
                      placeholder="Escribe tu comentario aquí..." 
                      maxlength="1000"></textarea><br>
            <button type="submit">Enviar Comentario</button>
        </form>
        
        <h2>Comentarios recibidos:</h2>
        {% if comments %}
            {% for comment in comments %}
                <div class="comment">
                    <div class="comment-meta">Comentario #{{ loop.index }}</div>
                    <div>{{ comment }}</div>
                </div>
            {% endfor %}
        {% else %}
            <div class="no-comments">No hay comentarios aún.</div>
        {% endif %}
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

# Almacenamiento en memoria (en producción usaría una base de datos)
comments_storage = []

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    
    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        
        # Validación de entrada
        if not comment:
            error = "El comentario no puede estar vacío."
        elif len(comment) > 1000:
            error = "El comentario no puede exceder los 1000 caracteres."
        else:
            # Sanitización: escape de HTML para prevenir XSS
            # Flask's render_template_string ya escapa por defecto, pero hacemos doble protección
            safe_comment = html.escape(comment)
            
            # Limitar el número de comentarios almacenados (prevención de DoS)
            if len(comments_storage) >= 100:
                comments_storage.pop(0)
            
            comments_storage.append(safe_comment)
    
    # Pasar comentarios a la plantilla (Flask escapa automáticamente)
    return render_template_string(HTML_TEMPLATE, comments=comments_storage, error=error)

if __name__ == '__main__':
    # Configuración segura para producción
    app.config.update(
        SECRET_KEY='clave-secreta-segura-y-compleja-aqui',  # En producción, usar variable de entorno
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # True en producción con HTTPS
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800  # 30 minutos
    )
    
    # En producción usar: app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(debug=True, host='127.0.0.1', port=5000)
