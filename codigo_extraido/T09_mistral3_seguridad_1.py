import os
from flask import Flask, request, jsonify, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import uuid
import imghdr
from functools import wraps
import re

app = Flask(__name__)

# Configuración segura
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'profile_images')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = os.urandom(24)  # Clave secreta aleatoria para producción

# Crear directorio de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Decorador para validar el tipo de contenido
def validate_content_type(allowed_types):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            content_type = file.content_type
            if content_type not in allowed_types:
                return jsonify({'error': f'Content type {content_type} not allowed'}), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator

# Validar extensión de archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Validar el contenido real de la imagen
def validate_image_content(file_stream):
    header = file_stream.read(32)
    file_stream.seek(0)
    file_type = imghdr.what(None, h=header)
    if file_type not in app.config['ALLOWED_EXTENSIONS']:
        return False
    return True

# Sanitizar nombre de usuario para usar en rutas
def sanitize_username(username):
    # Permitir solo caracteres alfanuméricos y guiones bajos
    return re.sub(r'[^\w\-]', '_', username)

@app.route('/api/upload_profile_image', methods=['POST'])
@validate_content_type(['image/png', 'image/jpeg', 'image/gif'])
def upload_profile_image():
    # Verificar autenticación (simplificado - en producción usar JWT o similar)
    if not request.headers.get('Authorization'):
        return jsonify({'error': 'Authentication required'}), 401

    # Obtener usuario del token (simplificado)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Invalid authorization header'}), 401

    # En producción, verificar el token JWT aquí
    username = "user_" + str(uuid.uuid4())[:8]  # Simulación de usuario autenticado

    # Validar archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File extension not allowed'}), 400

    # Validar contenido real de la imagen
    if not validate_image_content(file.stream):
        return jsonify({'error': 'Invalid image content'}), 400

    # Generar nombre de archivo seguro
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    sanitized_username = sanitize_username(username)
    safe_filename = f"{sanitized_username}_{unique_id}_{filename}"

    # Guardar archivo
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.seek(0)  # Asegurar que empezamos desde el principio
        file.save(file_path)

        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(file_path):
            return jsonify({'error': 'Failed to save file'}), 500

        # Verificar tamaño del archivo guardado
        file_size = os.path.getsize(file_path)
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            os.remove(file_path)
            return jsonify({'error': 'File size exceeds maximum limit'}), 400

        # Verificar que el archivo sigue siendo una imagen válida
        if not validate_image_content(open(file_path, 'rb')):
            os.remove(file_path)
            return jsonify({'error': 'Invalid image content after upload'}), 400

        # En producción, guardar la ruta en la base de datos asociada al usuario
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': safe_filename,
            'file_path': f'/profile_images/{safe_filename}'
        }), 201

    except Exception as e:
        current_app.logger.error(f'Error uploading file: {str(e)}')
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Configuración para producción (usar servidor WSGI en producción)
    app.run(host='0.0.0.0', port=5000, debug=False)
