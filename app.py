pythonfrom flask import Flask, request, jsonify
import base64
import tempfile
import os
import keep_alive

from router import detect_and_parse

app = Flask(__name__)
keep_alive.start()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/parse', methods=['POST'])
def parse():
    payload = request.get_json()
    b64 = payload.get('base64_pdf')
    doc_type = payload.get('doc_type', 'auto')  # FileMaker can pass a hint

    if not b64:
        return jsonify({'error': 'No base64_pdf provided'}), 400

    try:
        pdf_bytes = base64.b64decode(b64)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(pdf_bytes)
            tmp_path = f.name

        result = detect_and_parse(tmp_path, doc_type)
        os.unlink(tmp_path)
        return jsonify({'status': 'ok', 'data': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5055))
    app.run(host='0.0.0.0', port=port)
