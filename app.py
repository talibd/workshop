from flask import Flask, request, jsonify
import os

try:
    import openai
except ImportError:  # pragma: no cover - library may not be installed in CI
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def transcribe_file(file_path: str):
    """Transcribe the given audio or video file using the Whisper API."""
    if not openai:
        return {'error': 'openai library not installed'}
    if not OPENAI_API_KEY:
        return {'error': 'OPENAI_API_KEY not set'}

    with open(file_path, 'rb') as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
        )
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    transcript = transcribe_file(file_path)
    if 'error' in transcript:
        return jsonify(transcript), 500
    return jsonify(transcript), 200

if __name__ == '__main__':
    app.run(debug=True)
