from flask import Flask, request, jsonify, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
from functools import wraps

app = Flask(__name__)

# Configuración segura de la base de datos
DATABASE = os.path.join(app.instance_path, 'usuarios.db')
app.config['DATABASE'] = DATABASE
app.config['SECRET_KEY'] = os.urandom(24)  # Clave secreta aleatoria para sesiones

# Validación básica de nombre de usuario
def es_nombre_valido(nombre):
    """Valida que el nombre solo contenga caracteres permitidos."""
    return bool(re.match(r'^[a-zA-Z0-9_\-]{1,50}$', nombre))

# Decorador para manejar errores de base de datos
def manejar_errores_bd(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            app.logger.error(f"Error de base de datos: {e}")
            abort(500, description="Error interno del servidor")
    return decorated_function

# Función para obtener conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

# Inicializar la base de datos (solo para desarrollo, en producción debería existir)
def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Middleware para sanitizar entradas
@app.before_request
def sanitizar_entrada():
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json:
            data = request.get_json()
            if data:
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = value.strip()
        else:
            for key, value in request.form.items():
                if isinstance(value, str):
                    request.form[key] = value.strip()

# Endpoint para buscar usuario por nombre
@app.route('/api/usuario', methods=['GET'])
@manejar_errores_bd
def buscar_usuario():
    nombre = request.args.get('nombre')

    # Validación del parámetro
    if not nombre:
        abort(400, description="El parámetro 'nombre' es obligatorio")

    if not es_nombre_valido(nombre):
        abort(400, description="Nombre de usuario no válido")

    # Prevenir inyección SQL usando parámetros
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Usar parámetros para evitar inyección SQL
        query = "SELECT id, nombre, email, fecha_creacion FROM usuarios WHERE nombre = ?"
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()

        if not usuario:
            abort(404, description="Usuario no encontrado")

        # Convertir el resultado a un diccionario
        usuario_dict = dict(usuario)

        # Eliminar información sensible si existiera (aunque en este ejemplo no hay)
        usuario_dict.pop('password', None)  # Por si acaso existe la columna

        return jsonify(usuario_dict)

    except sqlite3.Error as e:
        app.logger.error(f"Error al buscar usuario: {e}")
        abort(500, description="Error al buscar usuario")
    finally:
        conn.close()

# Manejo de errores personalizado
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error.description)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error.description)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear directorio de instancia si no existe
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicializar la base de datos (solo para desarrollo)
    if not os.path.exists(app.config['DATABASE']):
        init_db()

    # Configuración segura para producción
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc',  # En producción usar certificados reales
        threaded=False,       # Para evitar problemas de concurrencia con SQLite
        debug=False           # Nunca activar debug en producción
    )
