from flask import Flask, request, redirect, url_for, session, render_template_string
from functools import wraps
import secrets
import urllib.parse

app = Flask(__name__)
# Configuración de seguridad
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Clave secreta robusta
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Solo HTTPS en producción
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos

# Simulación de base de datos de usuarios
USERS = {
    'usuario1': 'contraseña_segura_hash',
    'usuario2': 'otra_contraseña_hash'
}

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Redirigir a login con el parámetro next
            next_url = request.url
            return redirect(url_for('login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function

def is_safe_url(target):
    """Valida que la URL de redirección sea segura (mismo host)"""
    if not target:
        return False
    
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    
    # Verificar que sea misma red y mismo host
    return (test_url.scheme in ('http', 'https') and 
            ref_url.netloc == test_url.netloc)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    error = None
    next_url = request.args.get('next', '')
    
    # Validar URL de redirección
    if next_url and not is_safe_url(next_url):
        next_url = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones básicas
        if not username or not password:
            error = 'Usuario y contraseña son requeridos'
        elif len(username) > 50 or len(password) > 100:
            error = 'Datos de entrada demasiado largos'
        else:
            # En producción, aquí se verificaría contra base de datos con hash seguro
            # Esta es una simulación simplificada
            if username in USERS and password == USERS[username].replace('_hash', ''):
                # Autenticación exitosa
                session['username'] = username
                session.permanent = True
                
                # Redirigir a URL segura
                next_url = request.form.get('next', '')
                if next_url and is_safe_url(next_url):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            else:
                error = 'Credenciales inválidas'
    
    # Plantilla HTML segura (en producción usaría archivos .html)
    login_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inicio de Sesión</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h2>Iniciar Sesión</h2>
        {% if error %}<p style="color: red;"><strong>{{ error }}</strong></p>{% endif %}
        <form method="post">
            <input type="hidden" name="next" value="{{ next_url }}">
            <div>
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" maxlength="50" required>
            </div>
            <div>
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" maxlength="100" required>
            </div>
            <div>
                <button type="submit">Iniciar Sesión</button>
            </div>
        </form>
    </body>
    </html>
    '''
    
    return render_template_string(login_template, error=error, next_url=next_url)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Página protegida de ejemplo"""
    return f'<h1>Bienvenido {session["username"]}</h1><a href="/logout">Cerrar sesión</a>'

@app.route('/')
def index():
    """Página principal"""
    return '<h1>Página Principal</h1><a href="/dashboard">Dashboard</a>'

if __name__ == '__main__':
    # En producción, usar servidor WSGI como Gunicorn
    app.run(debug=False)  # debug=False en producción
