from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    comment = ""
    if request.method == 'POST':
        comment = request.form.get('comment', "")
        # Utiliza render_template_string con cuidado para evitar inyección de plantillas
        return render_template_string("<html><body><h1>Tu comentario:</h1><p>{{ comment|e }}</p></body></html>", comment=comment)
    return render_template_string("<html><body><form method='post'><label for='comment'>Escribe tu comentario:</label><input type='text' id='comment' name='comment'><input type='submit' value='Enviar'></form></body></html>")

if __name__ == '__main__':
    app.run(debug=True)
