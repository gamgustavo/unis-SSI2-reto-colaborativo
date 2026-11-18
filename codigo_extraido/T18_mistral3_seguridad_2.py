from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from urllib.parse import urlparse, urljoin
import functools

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aleatoria_y_segura'  # Debe ser una clave secreta fuerte y aleatoria

# Configuración de seguridad (recomendado para producción)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutos
)

# Base de datos simulada de usuarios (en producción, usa una base de datos real)
users = {
    'usuario1': {
        'password': 'pbkdf2:sha256:150000$...',  # Contraseña hasheada con werkzeug.security.generate_password_hash
        'role': 'user'
    }
}

def is_safe_redirect_url(target):
    """Verifica si la URL de redirección es segura para evitar open redirect attacks."""
    if not target:
        return False
    # Verifica que la URL sea relativa (empiece con '/')
    if target.startswith('/'):
        return True
    # Verifica que el dominio de la URL sea el mismo que el de la aplicación
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    """Obtiene el parámetro 'next' de la URL y verifica que sea seguro."""
    for target in request.args.get('next'), request.form.get('next'):
        if is_safe_redirect_url(target):
            return target
    return None

def login_required(view):
    """Decorador para requerir autenticación."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login', next=request.path))
        return view(**kwargs)
    return wrapped_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = get_redirect_target() or url_for('index')

        # Validación básica
        if not username or not password:
            flash('Nombre de usuario y contraseña son requeridos.', 'danger')
            return redirect(url_for('login', next=next_url))

        # Verificar usuario
        user = users.get(username)
        if not user or not check_password_hash(user['password'], password):
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login', next=next_url))

        # Autenticación exitosa
        session.clear()
        session['user_id'] = username
        session.permanent = True

        flash('Has iniciado sesión correctamente.', 'success')
        return redirect(next_url)

    # Método GET: mostrar formulario de login
    next_url = get_redirect_target()
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="hidden" name="next" value="{}">
            <button type="submit">Iniciar sesión</button>
        </form>
    '''.format(next_url if next_url else '')

@app.route('/')
def index():
    return 'Página de inicio'

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # En producción, usa un certificado SSL válido
