from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse, urljoin
import secrets
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Usuario de ejemplo (en producción usar una base de datos)
USERS = {
    'admin': generate_password_hash('password123')
}

def is_safe_url(target_url):
    """
    Valida que la URL de redirección sea segura (mismo host).
    Previene ataques de redirección abierta.
    """
    if not target_url:
        return False
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target_url))
    
    # Verificar que el esquema y el host sean seguros
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next', '')
        
        # Validación básica
        if not username or not password:
            return render_template_string('''
                <form method="POST">
                    <input type="text" name="username" placeholder="Usuario" required><br>
                    <input type="password" name="password" placeholder="Contraseña" required><br>
                    <input type="hidden" name="next" value="{{ next_url }}">
                    <button type="submit">Login</button>
                </form>
                <p style="color: red;">Usuario y contraseña requeridos</p>
            ''', next_url=next_url), 400
        
        # Autenticación
        user_hash = USERS.get(username)
        if user_hash and check_password_hash(user_hash, password):
            session.clear()
            session['user_id'] = username
            session.permanent = True
            
            # Validar y redirigir a la URL 'next' si es segura
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        
        # Autenticación fallida - mismo mensaje para evitar user enumeration
        return render_template_string('''
            <form method="POST">
                <input type="text" name="username" placeholder="Usuario" required><br>
                <input type="password" name="password" placeholder="Contraseña" required><br>
                <input type="hidden" name="next" value="{{ next_url }}">
                <button type="submit">Login</button>
            </form>
            <p style="color: red;">Credenciales inválidas</p>
        ''', next_url=next_url), 401
    
    # GET request - mostrar formulario
    next_url = request.args.get('next', '')
    return render_template_string('''
        <form method="POST">
            <input type="text" name="username" placeholder="Usuario" required><br>
            <input type="password" name="password" placeholder="Contraseña" required><br>
            <input type="hidden" name="next" value="{{ next_url }}">
            <button type="submit">Login</button>
        </form>
    ''', next_url=next_url)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))
    return f'Bienvenido {session["user_id"]}'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)  # debug=False en producción
