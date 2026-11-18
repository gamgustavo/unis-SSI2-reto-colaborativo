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
    if not name or len(name) > 100:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_\-\.\s]+$', name))

def get_db_connection():
    """Crea y retorna una conexión a la base de datos SQLite"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

@app.route('/usuario', methods=['GET'])
def get_usuario():
    # Validación del parámetro nombre
    nombre = request.args.get('nombre')
    if not nombre or not is_valid_name(nombre):
        raise BadRequest("Nombre inválido o no proporcionado")

    # Prevención de SQL Injection usando parámetros
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Usamos parámetros para evitar SQL Injection
        query = "SELECT id, nombre, email, fecha_registro FROM usuarios WHERE nombre = ?"
        cursor.execute(query, (nombre,))
        usuario = cursor.fetchone()

        if not usuario:
            raise NotFound("Usuario no encontrado")

        # Convertimos el resultado a un diccionario
        usuario_dict = dict(usuario)

        # Eliminamos información sensible si existiera (aunque en este ejemplo no hay)
        # En un caso real, podríamos tener campos como password_hash que no deberían devolverse

        return jsonify(usuario_dict)

    except sqlite3.Error as e:
        app.logger.error(f"Error de base de datos: {str(e)}")
        raise BadRequest("Error al procesar la solicitud")
    finally:
        if 'conn' in locals():
            conn.close()

# Manejo de errores personalizado
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Error interno: {str(error)}")
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    # Configuración de seguridad para producción
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc',  # En producción usar certificados reales
        threaded=False,       # Para evitar problemas con SQLite en entornos multiproceso
        debug=False           # Nunca activar debug en producción
    )
