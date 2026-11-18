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
            download_folder = 'descargas'
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)
            file_path = os.path.join(download_folder, file.filename)
            file.save(file_path)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(download_folder)
            return 'File successfully uploaded and extracted', 200
        except Exception as e:
            return str(e), 500
    else:
        return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True)
