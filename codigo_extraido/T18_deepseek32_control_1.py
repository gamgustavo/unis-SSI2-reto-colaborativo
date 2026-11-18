from flask import Flask, request, redirect, url_for, render_template_string, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave-secreta-para-sesiones'  # Necesaria para usar sesiones

# Simulación de base de datos de usuarios
USUARIOS = {'usuario1': 'contraseña1', 'usuario2': 'contraseña2'}

def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorador

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.args.get('next') or request.form.get('next') or url_for('index')
        
        if username in USUARIOS and USUARIOS[username] == password:
            session['username'] = username
            return redirect(next_url)
        else:
            return 'Credenciales inválidas', 401
    
    # GET: mostrar formulario de login
    next_url = request.args.get('next', url_for('index'))
    formulario_html = '''
        <form method="post">
            <input type="hidden" name="next" value="{{ next_url }}">
            <p>Usuario: <input type="text" name="username"></p>
            <p>Contraseña: <input type="password" name="password"></p>
            <p><input type="submit" value="Iniciar sesión"></p>
        </form>
    '''
    return render_template_string(formulario_html, next_url=next_url)

@app.route('/')
def index():
    return 'Página principal - <a href="/protegido">Área protegida</a>'

@app.route('/protegido')
@login_requerido
def protegido():
    return f'Área protegida - Hola {session["username"]}!'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
