from flask import Flask, request, send_file, abort
import os

app = Flask(__name__)
DOCUMENTS_FOLDER = 'documentos'

@app.route('/get-document', methods=['GET'])
def get_document():
    file_name = request.args.get('file_name')
    
    if not file_name:
        abort(400, description="El parámetro 'file_name' es requerido.")
    
    if '..' in file_name or file_name.startswith('/') or file_name.startswith('\\'):
        abort(400, description="Nombre de archivo no válido.")
    
    file_path = os.path.join(DOCUMENTS_FOLDER, file_name)
    
    if not os.path.isfile(file_path):
        abort(404, description="El archivo no se encontró.")
    
    return send_file(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
