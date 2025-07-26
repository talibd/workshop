# Flask Upload Example

This repository contains a simple Flask application with an `/upload` endpoint. The endpoint saves the uploaded video in the `uploads/` directory and transcribes it using the OpenAI Whisper API.

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Set the `OPENAI_API_KEY` environment variable before running the server so the
application can access the Whisper API:

```bash
export OPENAI_API_KEY=your-key-here
```

## Running the app

```bash
python app.py
```

The server will start on `http://localhost:5000`.

## Usage

Send a POST request with `multipart/form-data` containing the `file` field:

```bash
curl -F "file=@path/to/video.mp4" http://localhost:5000/upload
```
The server responds with the JSON transcription result, including the full text
and timestamped segments. The file is also saved in the `uploads/` directory.

## Keyword Extraction

The `keywords.py` module provides an `extract_keywords` function that uses spaCy
to find the most frequent nouns and verbs in a transcript. Example:

```python
from keywords import extract_keywords

text = "The quick brown fox jumps over the lazy dog."
print(extract_keywords(text))
```

The function requires the `en_core_web_sm` model to be installed:

```bash
python -m spacy download en_core_web_sm
```

## Unsplash Image Fetching

Set the `UNSPLASH_ACCESS_KEY` environment variable to allow the application to
retrieve one image from Unsplash for each extracted keyword when uploading a
file. The `/upload` response will then include a list of keywords and a mapping
of those keywords to image URLs.

```bash
export UNSPLASH_ACCESS_KEY=your-unsplash-key
```

## Video Rendering with FFmpeg

The `/render` endpoint now accepts a video file, an `.srt` subtitle file and
optionally multiple overlay images. Styling options for the subtitles can be
specified using form fields. All data should be sent as `multipart/form-data`:

```bash
curl -X POST http://localhost:5000/render \
  -F "video=@path/to/video.mp4" \
  -F "subtitles=@path/to/captions.srt" \
  -F "images=@path/to/overlay1.jpg" \
  -F "images=@path/to/overlay2.jpg" \
  -F "fontSize=32" \
  -F "fontColor=#ff0000" \
  -F "position=top"
```

The response contains the path to the rendered video in `static/exports`.

### Preview Clips

The `backend/ffmpeg_utils.py` module also exposes a
`generate_preview_clip` function for creating short clips from any point
in a video. Provide the timestamp where the clip should start along
with optional overlay images. The function outputs a 10‑second segment
with burned subtitles and b‑roll overlays.

```python
from ffmpeg_utils import generate_preview_clip

generate_preview_clip(
    "source.mp4",
    "captions.srt",
    [("overlay.jpg", 2, 3)],
    timestamp=30,
    output_path="preview.mp4",
)
```

