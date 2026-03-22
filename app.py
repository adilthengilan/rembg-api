from flask import Flask, request, send_file, make_response
from rembg import remove
import io
import os

app = Flask(__name__)

# ── Allow ALL origins explicitly ─────────────────────────────
ALLOWED_ORIGINS = [
    'http://localhost:57022',
    'http://localhost:5000',
    'https://rembg-api-94wh.onrender.com',
    '*'  # allow everything
]

def add_cors_headers(response):
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        return add_cors_headers(response)
    return {'status': 'ok'}, 200

@app.route('/remove-bg', methods=['POST', 'OPTIONS'])
def remove_bg():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        return add_cors_headers(response)

    try:
        if 'image' not in request.files:
            return {'error': 'No image provided'}, 400

        input_bytes = request.files['image'].read()

        if len(input_bytes) == 0:
            return {'error': 'Empty image'}, 400

        output_bytes = remove(input_bytes)

        response = make_response(
            send_file(
                io.BytesIO(output_bytes),
                mimetype='image/png'
            )
        )
        return add_cors_headers(response)

    except Exception as e:
        print(f'Error processing image: {e}')
        return {'error': str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)