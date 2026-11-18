from flask import Flask, request, redirect, url_for, render_template_string, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave-secreta-para-sesiones'  # Cambiar en producción

# Simulación de base de usuarios
USUARIOS = {'usuario1': 'contraseña1', 'usuario2': 'contraseña2'}

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
        next_url = request.form.get('next') or request.args.get('next')
        
        if username in USUARIOS and USUARIOS[username] == password:
            session['username'] = username
            if next_url:
                return redirect(next_url)
            return redirect(url_for('index'))
        return 'Credenciales inválidas', 401
    
    # GET: Mostrar formulario de login
    next_url = request.args.get('next', '')
    return render_template_string('''
        <form method="post">
            <input type="text" name="username" placeholder="Usuario" required><br>
            <input type="password" name="password" placeholder="Contraseña" required><br>
            <input type="hidden" name="next" value="{{ next_url }}">
            <button type="submit">Iniciar sesión</button>
        </form>
    ''', next_url=next_url)

@app.route('/')
@login_required
def index():
    return f'Hola, {session["username"]}!'

@app.route('/ruta-protegida')
@login_required
def ruta_protegida():
    return 'Contenido protegido'

if __name__ == '__main__':
    app.run(debug=True)
