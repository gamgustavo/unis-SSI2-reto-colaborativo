from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/fetch_url', methods=['POST'])
def fetch_url():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Se requiere un campo "url" en el JSON'}), 400
        
        url = data['url']
        
        # Validación básica de URL
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return jsonify({'error': 'URL no válida'}), 400
        
        # Descargar contenido
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Determinar el tipo de contenido
        content_type = response.headers.get('Content-Type', 'text/html')
        
        return jsonify({
            'url': url,
            'content': response.text,
            'content_type': content_type,
            'status_code': response.status_code,
            'headers': dict(response.headers)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al descargar la URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
