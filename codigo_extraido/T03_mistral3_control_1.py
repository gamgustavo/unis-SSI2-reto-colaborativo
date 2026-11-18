from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

@app.route('/documento/<nombre_archivo>', methods=['GET'])
def obtener_documento(nombre_archivo):
    carpeta_documentos = 'documentos'

    if not os.path.exists(carpeta_documentos):
        return jsonify({'error': 'La carpeta de documentos no existe'}), 404

    try:
        return send_from_directory(carpeta_documentos, nombre_archivo, as_attachment=False)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
