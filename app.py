from flask import Flask, request, send_file, make_response, jsonify
from rembg import remove, new_session
from PIL import Image
import io
import os

app = Flask(__name__)

# 🔥 Lazy load model
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


# ✅ Remove Background API
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    global SESSION

    try:
        input_bytes = None

        # ✅ Multipart (Mobile)
        if 'image' in request.files:
            input_bytes = request.files['image'].read()

        # ✅ Raw bytes (Web)
        else:
            raw = request.get_data()
            if raw:
                input_bytes = raw

        if not input_bytes:
            return jsonify({'error': 'No image provided'}), 400

        print(f"📥 Received: {len(input_bytes)} bytes")

        # 🔥 Hard size limit (Render safe)
        if len(input_bytes) > 1 * 1024 * 1024:  # 1MB
            return jsonify({'error': 'Image too large (max 1MB)'}), 400

        # 🔥 Open + Resize (CRITICAL FIX)
        try:
            img = Image.open(io.BytesIO(input_bytes)).convert("RGB")
            img.thumbnail((1024, 1024))  # reduce memory usage

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            input_bytes = buffer.getvalue()

        except Exception:
            return jsonify({'error': 'Invalid image'}), 400

        # 🔥 Lazy load model
        if SESSION is None:
            print("🚀 Loading model (u2netp)...")
            SESSION = new_session('u2netp')
            print("✅ Model ready!")

        # 🔥 Process (optimized)
        output_bytes = remove(
            input_bytes,
            session=SESSION,
            alpha_matting=False,
            post_process_mask=False  # 🔥 reduces RAM usage
        )

        print("✅ Processed successfully")

        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png'
        )

    except MemoryError:
        SESSION = None
        return jsonify({'error': 'Out of memory'}), 503

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({'error': 'Internal server error'}), 500


# ✅ Local run
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)