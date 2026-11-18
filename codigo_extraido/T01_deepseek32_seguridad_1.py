from flask import Flask, request, jsonify
import sqlite3
import re

app = Flask(__name__)

def get_db_connection():
    """Establece conexión segura a la base de datos"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_input(nombre):
    """Valida y sanitiza el parámetro de entrada"""
    if not nombre:
        return False
    
    # Validar longitud máxima (ajustar según necesidades)
    if len(nombre) > 100:
        return False
    
    # Validar caracteres permitidos (solo letras, números, espacios y guiones)
    # Ajustar según los requisitos específicos de tu aplicación
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', nombre):
        return False
    
    return True

@app.route('/buscar_usuario', methods=['GET'])
def buscar_usuario():
    """Endpoint para buscar usuario por nombre"""
    # Obtener parámetro de la consulta
    nombre = request.args.get('nombre')
    
    # Validar que el parámetro existe
    if not nombre:
        return jsonify({'error': 'El parámetro "nombre" es requerido'}), 400
    
    # Validar y sanitizar entrada
    if not validate_input(nombre):
        return jsonify({'error': 'Nombre no válido'}), 400
    
    try:
        # Conexión segura a la base de datos
        conn = get_db_connection()
        
        # Usar parámetros preparados para prevenir inyección SQL
        cursor = conn.execute(
            'SELECT id, nombre, email, fecha_creacion FROM usuarios WHERE nombre = ? LIMIT 1',
            (nombre,)
        )
        
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            # Convertir a diccionario para JSON
            usuario_dict = dict(usuario)
            return jsonify(usuario_dict), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except sqlite3.Error as e:
        # Log del error (en producción usar logging apropiado)
        app.logger.error(f'Error de base de datos: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500
        
    except Exception as e:
        # Capturar cualquier otro error inesperado
        app.logger.error(f'Error inesperado: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

# Configuración de seguridad adicional
@app.after_request
def add_security_headers(response):
    """Añadir cabeceras de seguridad HTTP"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # En producción, configurar CSP adecuadamente
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

if __name__ == '__main__':
    # En producción, usar servidor WSGI como Gunicorn
    # y desactivar debug mode
    app.run(debug=False, host='0.0.0.0', port=5000)
