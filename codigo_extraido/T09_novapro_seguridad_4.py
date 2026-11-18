from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import magic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    
    if not allowed_file(file.filename):
        return jsonify(error="File type not allowed"), 400
    
    mime = magic.Magic(mime=True)
    if mime.from_buffer(file.read()) not in ['image/png', 'image/jpeg', 'image/gif']:
        return jsonify(error="Invalid file type"), 400
    
    file.seek(0)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    return jsonify(message="File uploaded successfully", filename=filename), 201

if __name__ == '__main__':
    app.run(debug=True)
