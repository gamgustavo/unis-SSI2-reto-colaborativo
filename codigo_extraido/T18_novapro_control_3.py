from flask import Flask, request, redirect, url_for, render_template, session

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Cambia esto por una clave secreta segura

# Simulación de base de datos de usuarios
usuarios = {
    'usuario1': 'contraseña1',
    'usuario2': 'contraseña2'
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        
        if usuario in usuarios and usuarios[usuario] == contraseña:
            session['usuario'] = usuario
            next_page = request.args.get('next')
            return redirect(next_page or url_for('inicio'))
        else:
            return render_template('login.html', error='Credenciales inválidas')
    
    return render_template('login.html')

@app.route('/')
def inicio():
    if 'usuario' in session:
        return f'Bienvenido, {session["usuario"]}'
    return redirect(url_for('login', next=request.url))

if __name__ == '__main__':
    app.run(debug=True)
