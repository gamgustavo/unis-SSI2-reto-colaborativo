from flask import Flask, request, redirect, url_for, render_template_string, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Cambia esto en producción

# Simulación de base de usuarios
users = {'usuario': 'contraseña'}

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
        next_url = request.args.get('next') or request.form.get('next')
        
        if username in users and users[username] == password:
            session['username'] = username
            if next_url:
                return redirect(next_url)
            return redirect(url_for('index'))
        return 'Credenciales inválidas', 401
    
    # GET request - mostrar formulario
    next_url = request.args.get('next', '')
    return render_template_string('''
        <form method="post">
            <input type="hidden" name="next" value="{{ next_url }}">
            Usuario: <input type="text" name="username"><br>
            Contraseña: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''', next_url=next_url)

@app.route('/')
@login_required
def index():
    return f'Hola, {session["username"]}!'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
