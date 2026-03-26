from flask import Flask, request, send_file, make_response, jsonify
from rembg import remove, new_session
import io
import os

app = Flask(__name__)

# ❗ Do NOT load model at startup (important for Render)
SESSION = None


# ✅ Enable CORS
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


# ✅ Handle preflight
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response, 200


# ✅ Health route (Render uses this implicitly)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


# ✅ Background removal API
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    global SESSION

    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        input_bytes = file.read()

        if len(input_bytes) == 0:
            return jsonify({'error': 'Empty image'}), 400

        print(f"Processing image: {len(input_bytes)} bytes")

        # 🔥 Lazy load model (FIX FOR RENDER)
        if SESSION is None:
            print("Loading model (u2netp)...")
            SESSION = new_session('u2netp')
            print("Model loaded successfully!")

        # ✅ Process image (optimized)
        output_bytes = remove(
            input_bytes,
            session=SESSION,
            alpha_matting=False
        )

        print(f"Processed: {len(output_bytes)} bytes")

        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png',
            as_attachment=False
        )

    except MemoryError:
        SESSION = None
        return jsonify({'error': 'Out of memory'}), 503

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ✅ Local run (Render ignores this, uses gunicorn)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)