from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Crear directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-profile', methods=['POST'])
def upload_profile_picture():
    # Verificar si la petición tiene la parte de archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Verificar tipo de archivo
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generar nombre único para el archivo
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Guardar archivo
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Opcional: Aquí podrías guardar la referencia en tu base de datos
        # Por ejemplo: user.profile_picture = unique_filename
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'filepath': file_path
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
