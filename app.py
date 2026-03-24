from flask import Flask, request, send_file, make_response, jsonify
from rembg import remove, new_session
import io
import os

app = Flask(__name__)

# ── Use u2netp — tiny model (4MB), fits in 512MB RAM ────────
print('Loading rembg model...')
SESSION = new_session('u2netp')  # ← changed from u2net to u2netp
print('Model loaded!')
# ────────────────────────────────────────────────────────────

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response, 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        input_bytes = request.files['image'].read()

        if len(input_bytes) == 0:
            return jsonify({'error': 'Empty image'}), 400

        print(f'Processing: {len(input_bytes)} bytes')
        output_bytes = remove(input_bytes, session=SESSION)
        print(f'Done: {len(output_bytes)} bytes')

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