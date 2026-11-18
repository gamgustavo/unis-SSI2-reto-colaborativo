from flask import Flask, request, redirect, url_for, flash, render_template, session
from werkzeug.security import check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta segura

# Simulación de base de datos de usuarios
users_db = {
    'user1': {'password': 'pbkdf2:sha256:500000$aTnT7EXAMPLE$710fb8f945e60378e49EXAMPLE82aa7dfb43fa98b7f3d36e07a89f88a0'},
    'user2': {'password': 'pbkdf2:sha256:500000$aTnT7EXAMPLE$710fb8f945e60378e49EXAMPLE82aa7dfb43fa98b7f3d36e07a89f88a0'},
}

def is_safe_url(target):
    return all(url_part in request.host_url for url_part in url_for('static', filename='').split('/'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_db.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            next_page = request.args.get('next')
            if is_safe_url(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/')
def index():
    return "Welcome to the home page!"

if __name__ == '__main__':
    app.run(debug=True)
