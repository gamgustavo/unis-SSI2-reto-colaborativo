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
            zip_path = os.path.join('descargas', file.filename)
            file.save(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('descargas')
            os.remove(zip_path)
            return 'File successfully uploaded and extracted', 200
        except Exception as e:
            return str(e), 500
    else:
        return 'Invalid file type', 400

if __name__ == '__main__':
    if not os.path.exists('descargas'):
        os.makedirs('descargas')
    app.run(debug=True)
