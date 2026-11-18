from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_stream):
    """Valida que el archivo sea una imagen real verificando su cabecera"""
    file_type = imghdr.what(file_stream)
    return file_type in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """Sanitiza el nombre del archivo y genera uno único"""
    original_name = secure_filename(filename)
    name, ext = os.path.splitext(original_name)
    unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
    return unique_filename

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    """
    Endpoint para subir imágenes de perfil
    """
    # Verificar que la solicitud tenga el campo 'file'
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo en la solicitud'}), 400
    
    file = request.files['file']
    
    # Verificar que se haya seleccionado un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Validar extensión del archivo
    if not allowed_file(file.filename):
        return jsonify({'error': f'Extensión no permitida. Extensiones válidas: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # Validar que sea una imagen real
        file.seek(0)
        if not validate_image(file):
            return jsonify({'error': 'El archivo no es una imagen válida'}), 400
        
        # Sanitizar y generar nombre único
        file.seek(0)
        filename = sanitize_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Guardar archivo
        file.save(filepath)
        
        # Verificar integridad de la imagen
        try:
            with Image.open(filepath) as img:
                img.verify()  # Verifica que sea una imagen válida
        except Exception:
            # Si la imagen está corrupta, eliminar el archivo
            os.remove(filepath)
            return jsonify({'error': 'La imagen está corrupta'}), 400
        
        # Opcional: Redimensionar imagen si es muy grande
        with Image.open(filepath) as img:
            if img.size[0] > 2000 or img.size[1] > 2000:
                img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=85)
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'filename': filename,
            'path': filepath
        }), 201
        
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        app.logger.error(f'Error al subir imagen: {str(e)}')
        return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Configuración para producción
    app.run(debug=False, host='0.0.0.0', port=5000)
