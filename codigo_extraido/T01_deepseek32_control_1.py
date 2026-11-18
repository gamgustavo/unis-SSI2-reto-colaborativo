from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Ruta de la base de datos (se creará en el mismo directorio)
DATABASE = 'usuarios.db'

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT,
            edad INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/buscar_usuario', methods=['GET'])
def buscar_usuario():
    """Endpoint para buscar usuario por nombre"""
    nombre = request.args.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'El parámetro "nombre" es requerido'}), 400
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM usuarios WHERE nombre = ?', (nombre,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            # Convertir el objeto Row a diccionario
            usuario_dict = dict(usuario)
            return jsonify(usuario_dict)
        else:
            return jsonify({'mensaje': f'Usuario "{nombre}" no encontrado'}), 404
            
    except sqlite3.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

if __name__ == '__main__':
    # Inicializar la base de datos al iniciar la aplicación
    init_db()
    app.run(debug=True, port=5000)
