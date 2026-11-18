from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB límite
app.config['UPLOAD_FOLDER'] = 'uploads/profiles'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ALLOWED_MIME_TYPES'] = {'image/jpeg', 'image/png', 'image/gif'}

# Crear directorio de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_image(file_stream):
    """Valida que el archivo sea realmente una imagen usando la cabecera"""
    file_type = imghdr.what(file_stream)
    return file_type in app.config['ALLOWED_EXTENSIONS']

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
    
    # Verificar tipo de archivo por extensión
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido. Use PNG, JPG, JPEG o GIF'}), 400
    
    # Verificar tipo MIME
    if file.mimetype not in app.config['ALLOWED_MIME_TYPES']:
        return jsonify({'error': 'Tipo MIME no permitido'}), 400
    
    try:
        # Validar que sea realmente una imagen
        file.stream.seek(0)
        if not validate_image(file.stream):
            return jsonify({'error': 'El archivo no es una imagen válida'}), 400
        
        # Resetear el stream para guardar
        file.stream.seek(0)
        
        # Sanitizar y generar nombre único
        safe_filename = sanitize_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        # Guardar archivo
        file.save(filepath)
        
        # Verificar integridad de la imagen
        try:
            with Image.open(filepath) as img:
                img.verify()  # Verificar integridad
        except Exception:
            # Si la imagen está corrupta, eliminar el archivo
            os.remove(filepath)
            return jsonify({'error': 'La imagen está corrupta'}), 400
        
        # Opcional: Redimensionar imagen para prevenir ataques de recursos
        try:
            with Image.open(filepath) as img:
                # Verificar dimensiones máximas (opcional)
                max_size = (2000, 2000)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
        except Exception as e:
            app.logger.error(f"Error procesando imagen: {str(e)}")
            # Continuar incluso si el procesamiento falla
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'filename': safe_filename,
            'filepath': filepath
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error en upload: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Configuración de producción
    app.run(debug=False, host='0.0.0.0', port=5000)
