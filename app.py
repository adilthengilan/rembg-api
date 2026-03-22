from flask import Flask, request, send_file, make_response, jsonify
from rembg import remove
import io
import os

app = Flask(__name__)

# ── Add CORS to every single response ───────────────────────
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# ── Handle ALL preflight OPTIONS requests globally ──────────
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response, 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        input_bytes = file.read()

        if len(input_bytes) == 0:
            return jsonify({'error': 'Empty image'}), 400

        print(f'Processing image: {len(input_bytes)} bytes')

        output_bytes = remove(input_bytes)

        print(f'Done. Output: {len(output_bytes)} bytes')

        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png',
            as_attachment=False
        )

    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

