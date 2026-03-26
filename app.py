from flask import Flask, request, send_file, make_response, jsonify
from rembg import remove, new_session
from PIL import Image
import io
import os

app = Flask(__name__)

# ❗ Lazy load model (important for Render)
SESSION = None


# ✅ CORS
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


# ✅ Preflight
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response, 200


# ✅ Health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


# ✅ Remove background API
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    global SESSION

    try:
        # 🔹 Check file exists
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        input_bytes = file.read()

        # 🔹 Empty check
        if len(input_bytes) == 0:
            return jsonify({'error': 'Empty image'}), 400

        # 🔹 Size limit (IMPORTANT for Render)
        if len(input_bytes) > 2 * 1024 * 1024:  # 2MB
            return jsonify({'error': 'Image too large (max 2MB)'}), 400

        # 🔹 Validate image
        try:
            Image.open(io.BytesIO(input_bytes))
        except Exception:
            return jsonify({'error': 'Invalid image file'}), 400

        print(f"Processing image: {len(input_bytes)} bytes")

        # 🔥 Lazy load model
        if SESSION is None:
            print("Loading model (u2netp)...")
            SESSION = new_session('u2netp')
            print("Model loaded!")

        # 🔥 Process
        output_bytes = remove(
            input_bytes,
            session=SESSION,
            alpha_matting=False
        )

        print(f"Processed successfully: {len(output_bytes)} bytes")

        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png',
            as_attachment=False
        )

    except MemoryError:
        SESSION = None
        return jsonify({'error': 'Out of memory'}), 503

    except Exception as e:
        print("🔥 ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ✅ Local run (Render uses gunicorn)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)