from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    comment = ""
    if request.method == 'POST':
        comment = request.form.get('comment', "")
        # Sanitizar la entrada para prevenir XSS
        comment = comment.replace("<", "&lt;").replace(">", "&gt;")
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comentario del Usuario</title>
    </head>
    <body>
        <h1>Deja tu comentario:</h1>
        <form method="post">
            <textarea name="comment" rows="4" cols="50">{{ comment }}</textarea><br>
            <input type="submit" value="Enviar">
        </form>
        {% if comment %}
            <h2>Tu comentario:</h2>
            <p>{{ comment }}</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(template, comment=comment)

if __name__ == '__main__':
    app.run(debug=True)
