import os
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración
DOCUMENTS_FOLDER = 'documentos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md', 'csv', 'json', 'xml'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB límite

# Validar extensión del archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Validar ruta segura
def is_safe_path(base_path, target_path):
    # Resolver la ruta relativa y asegurar que esté dentro del directorio base
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(os.path.join(base_path, target_path))
    return abs_target.startswith(abs_base)

@app.route('/get_file', methods=['GET'])
def get_file():
    """
    Endpoint para obtener el contenido de un archivo.
    Parámetro: filename (nombre del archivo)
    """
    try:
        # Obtener el nombre del archivo del parámetro de consulta
        filename = request.args.get('filename')
        
        # Validar que se proporcionó un nombre de archivo
        if not filename:
            return jsonify({'error': 'Nombre de archivo no proporcionado'}), 400
        
        # Sanitizar el nombre del archivo
        safe_filename = secure_filename(filename)
        
        # Validar que el nombre sanitizado no esté vacío
        if not safe_filename:
            return jsonify({'error': 'Nombre de archivo inválido'}), 400
        
        # Validar extensión permitida
        if not allowed_file(safe_filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Construir la ruta completa del archivo
        file_path = os.path.join(DOCUMENTS_FOLDER, safe_filename)
        
        # Validar que la ruta sea segura (path traversal protection)
        if not is_safe_path(DOCUMENTS_FOLDER, safe_filename):
            return jsonify({'error': 'Ruta de archivo no válida'}), 400
        
        # Verificar que el archivo exista
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Verificar que sea un archivo y no un directorio
        if not os.path.isfile(file_path):
            return jsonify({'error': 'La ruta especificada no es un archivo'}), 400
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'Archivo demasiado grande'}), 413
        
        # Leer y devolver el contenido del archivo
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            return jsonify({
                'filename': safe_filename,
                'content': content,
                'size': file_size
            }), 200
            
        except UnicodeDecodeError:
            # Si no se puede leer como texto, devolver como archivo binario
            return send_file(
                file_path,
                as_attachment=False,
                download_name=safe_filename,
                mimetype='application/octet-stream'
            )
            
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        app.logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Configuración adicional de seguridad
@app.after_request
def add_security_headers(response):
    # Headers de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

if __name__ == '__main__':
    # Crear la carpeta documentos si no existe
    if not os.path.exists(DOCUMENTS_FOLDER):
        os.makedirs(DOCUMENTS_FOLDER)
    
    # Configuración para entorno de desarrollo
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    app.run(debug=False, host='0.0.0.0', port=5000)
