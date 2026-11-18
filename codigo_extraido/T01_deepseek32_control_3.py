from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Ruta para buscar usuario por nombre
@app.route('/buscar_usuario', methods=['GET'])
def buscar_usuario():
    nombre = request.args.get('nombre')
    
    if not nombre:
        return jsonify({'error': 'El parámetro "nombre" es requerido'}), 400
    
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        cursor = conn.cursor()
        
        # Buscar usuario por nombre (búsqueda exacta)
        cursor.execute('SELECT * FROM usuarios WHERE nombre = ?', (nombre,))
        usuario = cursor.fetchone()
        
        conn.close()
        
        if usuario:
            # Convertir fila SQLite a diccionario
            usuario_dict = dict(usuario)
            return jsonify(usuario_dict)
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except sqlite3.Error as e:
        return jsonify({'error': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

if __name__ == '__main__':
    # Crear base de datos y tabla de ejemplo si no existen
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT,
                edad INTEGER
            )
        ''')
        # Insertar datos de ejemplo
        cursor.execute("INSERT INTO usuarios (nombre, email, edad) VALUES ('Juan', 'juan@example.com', 30)")
        cursor.execute("INSERT INTO usuarios (nombre, email, edad) VALUES ('Maria', 'maria@example.com', 25)")
        conn.commit()
        conn.close()
        print("Base de datos y datos de ejemplo creados")
    
    app.run(debug=True, port=5000)
