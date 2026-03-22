from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove
import io
import os

app = Flask(__name__)
CORS(app)  # ← fixes Flutter Web "Failed to fetch" error

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400
    
    input_bytes = request.files['image'].read()
    output_bytes = remove(input_bytes)
    
    return send_file(
        io.BytesIO(output_bytes),
        mimetype='image/png'
    )

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)