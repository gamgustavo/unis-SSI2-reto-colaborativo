from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Bienvenido a la aplicación Flask segura"), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, ssl_context=('path/to/cert.pem', 'path/to/key.pem'))
