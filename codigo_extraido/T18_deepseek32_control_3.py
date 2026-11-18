from flask import Flask, request, redirect, url_for, render_template_string, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Cambia esto en producción

# Simulación de base de usuarios
USERS = {
    'admin': 'password123',
    'user': 'mypassword'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_page = request.args.get('next') or request.form.get('next')
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            # Redirigir a 'next' si existe y es seguro, sino a la página principal
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('index'))
        
        return render_template_string('''
            <form method="post">
                <input type="hidden" name="next" value="{{ next }}">
                Usuario: <input type="text" name="username"><br>
                Contraseña: <input type="password" name="password"><br>
                <input type="submit" value="Login">
                <p style="color:red">Credenciales incorrectas</p>
            </form>
        ''', next=next_page)
    
    # GET request
    next_page = request.args.get('next')
    return render_template_string('''
        <form method="post">
            <input type="hidden" name="next" value="{{ next }}">
            Usuario: <input type="text" name="username"><br>
            Contraseña: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''', next=next_page)

def is_safe_url(target):
    """Valida que la URL de redirección sea segura (mismo host)"""
    from urllib.parse import urlparse, urljoin
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/')
@login_required
def index():
    return f'Bienvenido {session["username"]}!'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected():
    return 'Esta es una página protegida'

if __name__ == '__main__':
    app.run(debug=True)
