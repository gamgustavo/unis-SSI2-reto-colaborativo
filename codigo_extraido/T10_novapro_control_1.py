from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/download-page', methods=['GET'])
def download_page():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        return jsonify({"content": response.text})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
