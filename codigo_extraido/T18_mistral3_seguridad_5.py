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
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# Decorador para requerir autenticación
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('user_id'):
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login', next=request.url))
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
            flash('Nombre de usuario y contraseña son requeridos.', 'danger')
            return redirect(url_for('login', next=next_url))

        # Aquí iría la lógica para verificar las credenciales contra tu base de datos
        # Ejemplo con datos ficticios (reemplazar con tu lógica real)
        user = get_user_from_database(username)  # Función hipotética para obtener usuario

        if user and check_password_hash(user['password_hash'], password):
            # Autenticación exitosa
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True

            # Redirección segura
            if next_url and is_safe_redirect_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')

    # Para GET, mostrar el formulario de login
    next_url = request.args.get('next')
    if next_url and not is_safe_redirect_url(next_url):
        next_url = None  # Ignorar URLs no seguras

    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="hidden" name="next" value="{}">
            <button type="submit">Iniciar sesión</button>
        </form>
    '''.format(next_url if next_url else '')

# Función hipotética para obtener usuario (reemplazar con tu implementación real)
def get_user_from_database(username):
    # Ejemplo con datos ficticios
    users = {
        'admin': {
            'id': 1,
            'password_hash': generate_password_hash('securepassword123')  # Usar contraseñas seguras en producción
        }
    }
    return users.get(username)

@app.route('/dashboard')
@login_required
def dashboard():
    return 'Bienvenido a tu dashboard'

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Usar HTTPS en desarrollo (en producción usar certificado válido)
