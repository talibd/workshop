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

The `/render` endpoint accepts subtitle style options which are passed directly
to FFmpeg. Send a JSON payload containing at least `video` and `subtitles` along
with optional `fontSize`, `fontColor` and `position` keys:

```bash
curl -X POST http://localhost:5000/render \
  -H 'Content-Type: application/json' \
  -d '{"video": "video.mp4", "subtitles": "captions.srt", "fontSize": 32, "fontColor": "#ff0000", "position": "top"}'
```

The response contains the path to the rendered video in `static/exports`.
