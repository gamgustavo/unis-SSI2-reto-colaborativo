from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from urllib.parse import urlparse, urljoin
import functools

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aleatoria_y_segura'  # Debe ser una clave secreta fuerte y única en producción

# Configuración de seguridad recomendada
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Solo enviar cookies sobre HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Evitar acceso a cookies desde JavaScript
    SESSION_COOKIE_SAMESITE='Lax',   # Protección contra CSRF
    PERMANENT_SESSION_LIFETIME=1800  # Tiempo de vida de la sesión en segundos
)

# Función para verificar si una URL es segura para redirección
def is_safe_redirect_url(target):
    if not target:
        return False
    # Verificar que la URL sea relativa o pertenezca al mismo dominio
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return (redirect_url.scheme in ('http', 'https') and
            host_url.netloc == redirect_url.netloc)

# Decorador para requerir autenticación
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login', next=request.path))
        return view(**kwargs)
    return wrapped_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.form.get('next')

        # Validación básica de entrada
        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'danger')
            return redirect(url_for('login', next=next_url))

        # Aquí iría la lógica real de autenticación (ejemplo simplificado)
        # En producción, usa consultas parametrizadas para evitar SQL injection
        # user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        user = {'id': 1, 'username': 'admin', 'password_hash': check_password_hash('hashed_password', password)}

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login', next=next_url))

        # Autenticación exitosa
        session.clear()
        session['user_id'] = user['id']
        session.permanent = True

        # Redirección segura
        if next_url and is_safe_redirect_url(next_url):
            return redirect(next_url)
        return redirect(url_for('index'))

    # GET request
    next_url = request.args.get('next')
    if next_url and not is_safe_redirect_url(next_url):
        next_url = None
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="hidden" name="next" value="{}">
            <button type="submit">Iniciar sesión</button>
        </form>
    '''.format(next_url if next_url else url_for('index'))

@app.route('/')
@login_required
def index():
    return 'Página de inicio - Usuario autenticado'

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # En producción, usa un certificado SSL válido
