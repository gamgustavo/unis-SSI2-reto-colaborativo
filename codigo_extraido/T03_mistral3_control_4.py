from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/documento/<nombre_archivo>', methods=['GET'])
def obtener_documento(nombre_archivo):
    directorio_documentos = 'documentos'
    try:
        return send_from_directory(directorio_documentos, nombre_archivo)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo no encontrado'}), 404

if __name__ == '__main__':
    if not os.path.exists('documentos'):
        os.makedirs('documentos')
    app.run(debug=True)
