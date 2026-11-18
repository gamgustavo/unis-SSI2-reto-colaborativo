from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB límite
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/profiles'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(stream):
    """Valida el tipo real del archivo usando su cabecera"""
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    # Verificar que la solicitud tenga el campo de archivo
    if 'profile_picture' not in request.files:
        return jsonify({'error': 'No se encontró el campo profile_picture'}), 400
    
    file = request.files['profile_picture']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Validar extensión del archivo
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    # Validar tipo real del archivo
    real_extension = validate_image(file.stream)
    if not real_extension:
        return jsonify({'error': 'Archivo no es una imagen válida'}), 400
    
    # Obtener extensión del nombre de archivo
    filename_ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Verificar coincidencia entre extensión real y declarada
    if real_extension != f'.{filename_ext}' and not (real_extension == '.jpg' and filename_ext == 'jpeg'):
        return jsonify({'error': 'Extensión del archivo no coincide con su tipo real'}), 400
    
    # Sanitizar nombre de archivo y generar nombre único
    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{real_extension}"
    
    # Ruta completa del archivo
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        # Procesar imagen para seguridad adicional
        img = Image.open(file.stream)
        
        # Convertir a RGB si es necesario (para PNG con transparencia)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionar si es muy grande (opcional, para seguridad)
        max_size = (2000, 2000)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar imagen procesada
        img.save(filepath, 'JPEG' if real_extension in ['.jpg', '.jpeg'] else img.format)
        
        # Cerrar la imagen
        img.close()
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'filename': unique_filename,
            'original_filename': original_filename
        }), 201
        
    except Exception as e:
        # Limpiar archivo si hubo error
        if os.path.exists(filepath):
            os.remove(filepath)
        app.logger.error(f'Error procesando imagen: {str(e)}')
        return jsonify({'error': 'Error procesando la imagen'}), 500

if __name__ == '__main__':
    # Configuración de producción
    app.run(debug=False, host='0.0.0.0', port=5000)
