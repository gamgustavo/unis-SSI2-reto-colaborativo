from flask import Flask, request, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aleatoria_y_segura'  # Debe ser larga y aleatoria en producción

# Función para validar URLs seguras (evita redirecciones abiertas)
def is_safe_redirect_url(target):
    if not target:
        return False
    # Asegura que la URL sea relativa o pertenezca al mismo dominio
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# Función para obtener la URL de redirección segura
def get_safe_redirect():
    next_url = request.args.get('next')
    if next_url and is_safe_redirect_url(next_url):
        return next_url
    return url_for('index')  # Redirige a una ruta segura por defecto

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Validación básica de entrada (evita campos vacíos)
        if not username or not password:
            abort(400, description="Usuario y contraseña son requeridos")

        # Aquí iría la lógica real de autenticación (ejemplo simplificado)
        # En producción, usa consultas parametrizadas para evitar SQLi
        user = get_user_from_db(username)  # Implementa esta función

        if user and check_password_hash(user['password_hash'], password):
            # Autenticación exitosa
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True  # Usa cookies persistentes si es necesario

            # Redirección segura
            next_url = get_safe_redirect()
            return redirect(next_url)
        else:
            abort(401, description="Credenciales inválidas")

    # Para GET, muestra el formulario de login
    next_url = request.args.get('next')
    if next_url and not is_safe_redirect_url(next_url):
        next_url = None  # Descarta URLs inseguras
    return render_template('login.html', next=next_url)

# Función de ejemplo para obtener usuario (implementa según tu modelo)
def get_user_from_db(username):
    # Ejemplo con SQLAlchemy (usa siempre consultas parametrizadas)
    # return User.query.filter_by(username=username).first()
    return {'id': 1, 'username': username, 'password_hash': generate_password_hash('contraseña_segura')}

# Ruta segura por defecto
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.path))
    return "Bienvenido a la página principal"

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Usa HTTPS en producción con certificados válidos
