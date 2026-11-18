from flask import Flask, redirect, request, url_for, session
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.args.get('next') or request.form.get('next')

        # Aquí deberías validar el usuario y contraseña con tu base de datos
        # Este es solo un ejemplo básico
        if username == 'admin' and check_password_hash('contraseña_hasheada', password):
            session['user'] = username

            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('index'))
        return "Credenciales inválidas", 401

    # Para GET, mostrar el formulario de login
    next_url = request.args.get('next')
    return f'''
        <form method="post">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="hidden" name="next" value="{next_url or ''}">
            <button type="submit">Iniciar sesión</button>
        </form>
    '''

def is_safe_url(target):
    from urllib.parse import urlparse, urljoin
    from flask import request

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/')
def index():
    return "Página principal"
