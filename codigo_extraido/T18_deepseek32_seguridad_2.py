from flask import Flask, request, redirect, url_for, session, render_template_string
from functools import wraps
import secrets
import urllib.parse

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Clave secreta segura para sesiones

# Simulación de base de datos de usuarios (en producción usaría una base de datos real)
USERS = {
    'usuario1': {'password': 'clave_segura_hash_123', 'id': 1},
    'usuario2': {'password': 'otro_hash_seguro_456', 'id': 2}
}

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Redirigir a login con el parámetro 'next' actual
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
    
    # Verificar que sea una URL válida y del mismo host
    return (test_url.scheme in ('http', 'https', '') and 
            ref_url.netloc == test_url.netloc)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión con soporte para parámetro 'next'"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        next_url = request.form.get('next', '')
        
        # Validación básica de entrada
        if not username or not password:
            return render_login_form(next_url, error="Usuario y contraseña requeridos")
        
        # Autenticación (en producción usaría bcrypt para comparar hashes)
        user = USERS.get(username)
        if user and user['password'] == password:  # Comparación simulada
            # Establecer sesión segura
            session.clear()
            session['user_id'] = user['id']
            session['username'] = username
            
            # Regenerar ID de sesión para prevenir fixation attacks
            session.regenerate()
            
            # Validar y redirigir a la URL 'next' si es segura
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        
        return render_login_form(next_url, error="Credenciales inválidas")
    
    # GET request - mostrar formulario
    next_url = request.args.get('next', '')
    return render_login_form(next_url)

def render_login_form(next_url='', error=''):
    """Renderiza el formulario de login de forma segura"""
    form_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Iniciar Sesión</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h2>Iniciar Sesión</h2>
        {% if error %}
            <p style="color: red;"><strong>Error:</strong> {{ error }}</p>
        {% endif %}
        <form method="POST" action="">
            <input type="hidden" name="next" value="{{ next_url }}">
            <div>
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div>
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div>
                <button type="submit">Iniciar Sesión</button>
            </div>
        </form>
    </body>
    </html>
    '''
    return render_template_string(form_html, next_url=next_url, error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    """Página protegida después del login"""
    return f'Bienvenido {session.get("username")}!'

@app.route('/logout')
def logout():
    """Cerrar sesión de forma segura"""
    session.clear()
    return redirect(url_for('login'))

# Configuración de seguridad adicional
@app.after_request
def add_security_headers(response):
    """Agrega headers de seguridad HTTP"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # En producción usar certificados reales
