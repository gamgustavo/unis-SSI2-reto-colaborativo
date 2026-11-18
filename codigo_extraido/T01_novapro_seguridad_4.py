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
    
    # Utilizando parámetros para evitar inyección SQL
    cursor.execute("SELECT * FROM usuarios WHERE nombre =?", (nombre,))
    usuario = cursor.fetchone()
    
    conn.close()
    
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Convirtiendo el resultado de la consulta a un diccionario
    usuario_dict = dict(usuario)
    
    return jsonify(usuario_dict)

if __name__ == '__main__':
    app.run(debug=True)
