from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_user_by_name(nombre):
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre =?", (nombre,))
        user = cursor.fetchone()
        connection.close()
        if user:
            return {"id": user[0], "nombre": user[1], "email": user[2]}
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

@app.route('/usuario', methods=['GET'])
def obtener_usuario():
    nombre = request.args.get('nombre')
    if not nombre:
        return jsonify({"error": "El parámetro 'nombre' es requerido"}), 400
    
    user = get_user_by_name(nombre)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
