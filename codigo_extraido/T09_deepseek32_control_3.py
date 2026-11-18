from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB límite

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Crear directorio si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    # Verificar si la petición tiene el archivo
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo en la petición'}), 400
    
    file = request.files['file']
    
    # Verificar si se seleccionó un archivo
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Verificar extensión permitida
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido. Use: png, jpg, jpeg, gif'}), 400
    
    # Generar nombre único para el archivo
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Guardar archivo
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Opcional: Aquí podrías guardar la referencia en tu base de datos
        # user.profile_picture = unique_filename
        # db.session.commit()
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'filename': unique_filename,
            'file_path': file_path
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al guardar el archivo: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
