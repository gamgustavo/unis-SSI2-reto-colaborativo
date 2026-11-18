import os
import zipfile
from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    if file and file.filename.endswith('.zip'):
        try:
            # Ensure the 'descargas' directory exists
            if not os.path.exists('descargas'):
                os.makedirs('descargas')
            
            # Save the uploaded file temporarily
            zip_path = os.path.join('descargas', file.filename)
            file.save(zip_path)
            
            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('descargas')
            
            # Remove the temporary ZIP file
            os.remove(zip_path)
            
            return 'File extracted successfully', 200
        
        except Exception as e:
            return str(e), 500
    
    return 'Invalid file', 400

if __name__ == '__main__':
    app.run(debug=True)
