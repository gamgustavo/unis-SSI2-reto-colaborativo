from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB límite
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/profiles'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    # Verificar que la solicitud tenga el archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó archivo'}), 400
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    # Validar extensión del archivo
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    # Validar tipo real del archivo
    real_extension = validate_image(file.stream)
    if not real_extension or real_extension[1:] not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Archivo no es una imagen válida'}), 400
    
    # Sanitizar el nombre del archivo
    original_filename = secure_filename(file.filename)
    
    # Generar nombre único para evitar colisiones y path traversal
    unique_filename = f"{uuid.uuid4().hex}{real_extension}"
    
    # Construir ruta segura
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    try:
        # Guardar archivo
        file.save(filepath)
        
        # Verificar y procesar la imagen
        try:
            with Image.open(filepath) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande (opcional)
                max_size = (2000, 2000)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Guardar imagen procesada
                img.save(filepath, 'JPEG' if real_extension == '.jpg' else img.format)
                
        except Exception as img_error:
            # Eliminar archivo si no es una imagen válida
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Error procesando la imagen'}), 400
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'filename': unique_filename,
            'url': f'/profile-pictures/{unique_filename}'
        }), 200
        
    except Exception as e:
        # Limpiar en caso de error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': 'Error al guardar la imagen'}), 500

@app.route('/profile-pictures/<filename>', methods=['GET'])
def get_profile_picture(filename):
    """Endpoint para servir imágenes de perfil (con validación de seguridad)"""
    # Prevenir path traversal
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        return jsonify({'error': 'Nombre de archivo inválido'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # Verificar que el archivo existe y es una imagen
    if not os.path.exists(filepath):
        return jsonify({'error': 'Imagen no encontrada'}), 404
    
    # Verificar que es un archivo regular (no un directorio o enlace simbólico)
    if not os.path.isfile(filepath):
        return jsonify({'error': 'Recurso no disponible'}), 403
    
    # Servir el archivo (en producción, usar servidor web como Nginx para archivos estáticos)
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)

if __name__ == '__main__':
    # En producción, usar un servidor WSGI como Gunicorn
    app.run(debug=False, host='0.0.0.0', port=5000)
