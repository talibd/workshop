from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

from keywords import extract_keywords
from unsplash_utils import fetch_images
from ffmpeg_utils import compose_video

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
    text = transcript.get('text', '') if isinstance(transcript, dict) else ''
    keywords = extract_keywords(text) if text else []
    images = fetch_images(keywords) if keywords else {}
    return jsonify({
        'transcript': transcript,
        'keywords': keywords,
        'images': images,
    }), 200


@app.route('/render', methods=['POST'])
def render_video():
    """Render a video with optional overlays and subtitle styling."""
    if 'video' not in request.files or 'subtitles' not in request.files:
        return jsonify({'error': 'video and subtitles required'}), 400

    video_file = request.files['video']
    subs_file = request.files['subtitles']
    if video_file.filename == '' or subs_file.filename == '':
        return jsonify({'error': 'empty filename provided'}), 400

    video_path = os.path.join(UPLOAD_FOLDER, secure_filename(video_file.filename))
    subs_path = os.path.join(UPLOAD_FOLDER, secure_filename(subs_file.filename))
    video_file.save(video_path)
    subs_file.save(subs_path)

    # Save optional overlay images
    overlays = []
    start = 0.0
    duration = 3.0
    for img in request.files.getlist('images'):
        if img.filename:
            img_path = os.path.join(UPLOAD_FOLDER, secure_filename(img.filename))
            img.save(img_path)
            overlays.append((img_path, start, duration))
            start += duration

    font_size = int(request.form.get('fontSize', 24))
    font_color = request.form.get('fontColor', '#ffffff')
    position = request.form.get('position', 'bottom')

    output_dir = os.path.join('static', 'exports')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'rendered.mp4')
    try:
        compose_video(
            video_path,
            subs_path,
            overlays,
            output_path=output_path,
            font_size=font_size,
            font_color=font_color,
            position=position,
        )
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500

    return jsonify({'output': output_path}), 200

if __name__ == '__main__':
    app.run(debug=True)
