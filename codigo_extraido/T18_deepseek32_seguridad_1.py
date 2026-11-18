from flask import Flask, request, redirect, url_for, session, render_template_string
from functools import wraps
import secrets
import urllib.parse

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Clave secreta segura para sesiones

# Simulación de base de datos de usuarios (en producción usaría una base de datos real)
USERS = {
    'usuario1': 'password1',
    'usuario2': 'password2'
}

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Guardar la URL actual para redirigir después del login
            next_url = request.url
            return redirect(url_for('login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function

def is_safe_url(target):
    """
    Valida que la URL de redirección sea segura.
    Evita ataques de redirección abierta.
    """
    if not target:
        return False
    
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    
    # Verificar que sea una URL relativa o del mismo dominio
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    error = None
    next_url = request.args.get('next', '')
    
    # Validar que la URL de redirección sea segura
    if next_url and not is_safe_url(next_url):
        next_url = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones básicas
        if not username or not password:
            error = 'Usuario y contraseña son requeridos'
        elif username not in USERS:
            error = 'Credenciales inválidas'
        elif USERS[username] != password:
            error = 'Credenciales inválidas'
        else:
            # Autenticación exitosa
            session['username'] = username
            
            # Redirigir a la URL segura o a la página principal
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('index'))
    
    # HTML simple para el formulario de login (en producción usaría templates)
    login_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
            .error { color: red; margin-bottom: 15px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input[type="text"], input[type="password"] { width: 100%; padding: 8px; box-sizing: border-box; }
            button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
        </style>
    </head>
    <body>
        <h2>Iniciar Sesión</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <input type="hidden" name="next" value="{{ next_url }}">
            <button type="submit">Iniciar Sesión</button>
        </form>
    </body>
    </html>
    '''
    
    return render_template_string(login_form, error=error, next_url=next_url)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    """Página principal protegida"""
    return f'<h1>Bienvenido, {session["username"]}!</h1><a href="/logout">Cerrar sesión</a>'

@app.route('/protegida')
@login_required
def protegida():
    """Otra página protegida"""
    return f'<h1>Página protegida</h1><p>Usuario: {session["username"]}</p><a href="/">Inicio</a>'

if __name__ == '__main__':
    # En producción, usar servidor WSGI como Gunicorn
    app.run(debug=False, host='0.0.0.0', port=5000)
