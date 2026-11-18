from flask import Flask, request, redirect, url_for, flash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key ='supersecretkey'

# Ejemplo de base de datos de usuarios
users = {
    'user1': 'pbkdf2:sha256:500000$6bA4n123$b69f98f5f5e89d9cf8f9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9e9',  # hash de 'password1'
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users.get(username), password):
            next_page = request.args.get('next')  # Obtener el parámetro 'next'
            return redirect(next_page or url_for('index'))  # Redirigir a 'next' o a la página de inicio si 'next' no está presente
        else:
            flash('Credenciales inválidas', 'error')
            return redirect(url_for('login'))
    
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/')
def index():
    return "Bienvenido a la página de inicio"

if __name__ == '__main__':
    app.run(debug=True)
