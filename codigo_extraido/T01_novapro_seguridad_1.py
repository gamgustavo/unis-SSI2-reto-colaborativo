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
    cursor = conn.cursor()
    
    query = "SELECT * FROM usuarios WHERE nombre =?"
    cursor.execute(query, (nombre,))
    
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    usuario_dict = {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "email": usuario["email"]
    }
    
    return jsonify(usuario_dict)

if __name__ == '__main__':
    app.run(debug=True)
