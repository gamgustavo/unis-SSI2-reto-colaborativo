from flask import Flask, request, redirect, url_for, flash, render_template, session
from werkzeug.security import check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_segura'  # Cambiar en producción

# Simulación de base de datos de usuarios
users_db = {
    'usuario1': 'hash_de_contraseña_segura1',
    'usuario2': 'hash_de_contraseña_segura2',
}

# Validación segura de URL
def is_safe_url(target):
    return all(url_part in request.host_url for url_part in re.split(r'[&?]', target))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users_db and check_password_hash(users_db[username], password):
            session['username'] = username
            next_page = request.args.get('next')
            if is_safe_url(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/')
def index():
    return "Bienvenido a la página de inicio"

if __name__ == '__main__':
    app.run(debug=True)
