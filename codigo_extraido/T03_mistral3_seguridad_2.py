import os
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración segura
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita el tamaño de archivo a 16MB
app.config['UPLOAD_FOLDER'] = 'documentos'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md'}  # Extensiones permitidas

# Verifica que la carpeta de documentos exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Verifica que el archivo tenga una extensión permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/documento/<filename>', methods=['GET'])
def get_document(filename):
    """Endpoint para obtener el contenido de un archivo de la carpeta 'documentos'."""
    # Sanitiza el nombre del archivo para evitar path traversal
    safe_filename = secure_filename(filename)

    if not safe_filename:
        abort(400, description="Nombre de archivo no válido")

    if not allowed_file(safe_filename):
        abort(400, description="Extensión de archivo no permitida")

    # Construye la ruta segura
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    # Verifica que el archivo exista y esté dentro de la carpeta permitida
    try:
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            abort(403, description="Acceso denegado")
    except (TypeError, ValueError):
        abort(400, description="Ruta de archivo no válida")

    if not os.path.isfile(file_path):
        abort(404, description="Archivo no encontrado")

    # Lee el archivo de forma segura
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except IOError:
        abort(500, description="Error al leer el archivo")

    # Determina el tipo MIME para la respuesta
    mime_type = 'application/octet-stream'
    if '.' in safe_filename:
        ext = safe_filename.rsplit('.', 1)[1].lower()
        mime_types = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'md': 'text/markdown'
        }
        mime_type = mime_types.get(ext, mime_type)

    return content, 200, {'Content-Type': mime_type, 'Content-Disposition': f'inline; filename={safe_filename}'}

if __name__ == '__main__':
    app.run(debug=False)  # Nunca usar debug=True en producción
