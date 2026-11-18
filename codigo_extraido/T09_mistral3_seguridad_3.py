import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

app = Flask(__name__)

# Configuración segura
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo
app.config['UPLOAD_FOLDER'] = 'static/profile_pictures'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_MIME_TYPES'] = {'image/png', 'image/jpeg', 'image/gif'}

# Crear directorio de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Verificar extensión y tipo MIME del archivo"""
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in app.config['ALLOWED_EXTENSIONS']:
        return False

    # Verificar tipo MIME real
    file_stream = request.files[filename].stream
    file_stream.seek(0)
    mime_type = imghdr.what(file_stream)
    if mime_type not in ['png', 'jpeg', 'gif']:
        return False

    return True

def validate_image(file_stream):
    """Validar que el archivo sea una imagen válida y no contenga código malicioso"""
    try:
        # Verificar que sea una imagen válida
        file_stream.seek(0)
        img = Image.open(file_stream)
        img.verify()  # Verifica la integridad del archivo

        # Verificar dimensiones para evitar DoS
        file_stream.seek(0)
        img = Image.open(file_stream)
        if img.width > 2000 or img.height > 2000:
            return False

        return True
    except (IOError, SyntaxError):
        return False

@app.route('/api/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    # Verificar que el request tenga el archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Verificar que el usuario seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Verificar seguridad del nombre de archivo
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type or extension'}), 400

    # Validar la imagen
    if not validate_image(file.stream):
        return jsonify({'error': 'Invalid or malicious image file'}), 400

    # Generar nombre seguro y único
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Guardar el archivo de forma segura
        file.stream.seek(0)
        file.save(filepath)

        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save file'}), 500

        # Verificar tamaño del archivo guardado
        if os.path.getsize(filepath) > app.config['MAX_CONTENT_LENGTH']:
            os.remove(filepath)
            return jsonify({'error': 'File size exceeds maximum limit'}), 400

        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'filename': filename,
            'url': f"/static/profile_pictures/{filename}"
        }), 201
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False)  # Nunca usar debug=True en producción
