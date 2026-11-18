from flask import Flask, jsonify

app = Flask(__name__)

# Configuración básica de seguridad
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_segura'
app.config['JSON_SORT_KEYS'] = False

# Ruta de inicio segura
@app.route('/', methods=['GET'])
def inicio():
    respuesta = {
       'mensaje': 'Bienvenido a la aplicación Flask segura',
        'estado': 'éxito'
    }
    return jsonify(respuesta), 200

# Ejecución segura de la aplicación
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
