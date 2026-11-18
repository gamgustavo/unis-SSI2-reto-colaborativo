from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'usuarios.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/usuario', methods=['GET'])
def obtener_usuario():
    nombre = request.args.get('nombre')
    if not nombre:
        return jsonify({"error": "El parámetro 'nombre' es requerido"}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre =?", (nombre,))
        usuario = cursor.fetchone()
        
        if usuario is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        usuario_dict = {
            "id": usuario['id'],
            "nombre": usuario['nombre'],
            "email": usuario['email']
        }
        return jsonify(usuario_dict), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Error al acceder a la base de datos", "details": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
