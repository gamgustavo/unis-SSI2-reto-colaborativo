from flask import Flask, request, jsonify
import sqlite3
from werkzeug.exceptions import NotFound, BadRequest
import re

app = Flask(__name__)

# Configuración de seguridad
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutos
)

# Validación de entrada
def is_valid_name(name):
    """Valida que el nombre solo contenga caracteres permitidos"""
    return bool(re.match(r'^[a-zA-Z0-9_\-\. ]{1,50}$', name))

def get_db_connection():
    """Crea y retorna una conexión a la base de datos SQLite"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

@app.route('/usuario', methods=['GET'])
def get_usuario():
    # Validación de Content-Type
    if not request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Content-Type no soportado'}), 406

    # Obtener y validar parámetro
    nombre = request.args.get('nombre')
    if not nombre:
        raise BadRequest('El parámetro "nombre" es requerido')

    if not is_valid_name(nombre):
        raise BadRequest('El nombre contiene caracteres no permitidos')

    # Prevenir inyección SQL usando parámetros
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Usar parámetros para evitar inyección SQL
        query = "SELECT id, nombre, email, fecha_registro FROM usuarios WHERE nombre = ?"
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()

        if not usuario:
            raise NotFound('Usuario no encontrado')

        # Convertir a diccionario para evitar exponer información sensible
        usuario_data = dict(usuario)

        # Eliminar campos sensibles si los hubiera (ejemplo)
        usuario_data.pop('password', None)

        return jsonify(usuario_data)

    except sqlite3.Error as e:
        app.logger.error(f"Error de base de datos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

    finally:
        if 'conn' in locals():
            conn.close()

# Manejo de errores personalizado
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Configuración segura para producción (usar en conjunto con un servidor WSGI)
    app.run(ssl_context='adhoc', host='0.0.0.0', port=5000)
