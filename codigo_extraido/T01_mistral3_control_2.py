from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/buscar_usuario', methods=['GET'])
def buscar_usuario():
    nombre = request.args.get('nombre')

    if not nombre:
        return jsonify({'error': 'El parámetro "nombre" es requerido'}), 400

    try:
        conn = sqlite3.connect('tu_base_de_datos.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,))
        usuario = cursor.fetchone()

        if usuario:
            # Asumiendo que la tabla tiene columnas: id, nombre, email, etc.
            columnas = [description[0] for description in cursor.description]
            usuario_dict = dict(zip(columnas, usuario))
            return jsonify(usuario_dict)
        else:
            return jsonify({'mensaje': 'Usuario no encontrado'}), 404

    except sqlite3.Error as e:
        return jsonify({'error': f'Error en la base de datos: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
